import logging
from datetime import datetime, timedelta

import transaction
from plone import api
from plone.base.interfaces import ILanguage
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.blocks import visit_blocks
from plone.restapi.deserializer.utils import path2uid
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

logger = logging.getLogger("eea.climateadapt")


class MigrateAbsoluteURLs(BrowserView):
    """Migrate absolute URLs to resolveuid"""

    fields = [
        "url",
        "href",
        "provider_url",
        "link",
        "getRemoteUrl",
        "attachedImage",
        "attachedimage",
        "getPath",
        "getURL",
        "preview_image",
        "@id",
    ]
    count = 0

    def fix_url(self, block):
        if isinstance(block, dict):  # If the current data is a dictionary
            for key, value in block.items():
                if key in self.fields:  # Check for the 'url' key with the target value
                    if value and isinstance(value, str):
                        cleaned_url = clean_url(value)

                        if cleaned_url != value:
                            block[key] = path2uid(
                                context=self.context, link=cleaned_url
                            )
                            self.count += 1
                else:
                    self.fix_url(value)  # Recursively check the value

        elif isinstance(block, list):  # If the current data is a list
            for item in block:
                self.fix_url(item)

    def migrate(self):
        """Migrate absolute URLs to resolveuid"""
        query = {
            "context": self.context,
            "object_provides": "plone.restapi.behaviors.IBlocks",
        }

        # Get the request object
        request = self.request

        # Read the 'days' parameter from the request
        days = request.get("days", None)

        # Convert 'days' to an integer if it is provided
        if days is not None:
            try:
                days = int(days)
            except ValueError:
                # Handle the case where 'days' is not a valid integer
                days = None

        if days is not None:
            # Calculate the date `days` ago from today
            date = datetime.now() - timedelta(days=days)

            # Add the modified filter to the query
            query["modified"] = {"query": date, "range": "min"}

        brains = api.content.find(**query)

        total = len(brains)
        for idx, brain in enumerate(brains):
            obj = brain.getObject()
            # if obj.title == "Discover the key services, thematic features and tools of Climate-ADAPT":
            #     import pdb; pdb.set_trace()
            blocks = getattr(obj, "blocks", {})
            # blocks_orig = copy.deepcopy(blocks)

            if "localhost" in str(
                blocks
            ) or "https://climate-adapt.eea.europa.eu" in str(blocks):
                for block in visit_blocks(obj, blocks):
                    self.fix_url(block)

                try:
                    modified(obj)
                except Exception as e:
                    logger.error("Failed to update %s: %s", brain.getURL(), e)

            if idx % 100 == 0:
                transaction.commit()
                logger.info("Progress %s of %s. Migrated %s", idx, total, self.count)

        return self.count

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        count = self.migrate()
        IStatusMessage(self.request).addStatusMessage(
            "Migrated {} absolute URLs!".format(count)
        )
        return self.request.response.redirect(self.context.absolute_url())


class FixMipSigLangs(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        catalog = self.context.portal_catalog
        brains = catalog.unrestrictedSearchResults(
            path="/cca/en", portal_type="mission_signatory_profile"
        )
        for brain in brains:
            obj = brain.getObject()
            ILanguage(obj).set_language("en")
            catalog.reindexObject(obj, idxs=["Language"])
            logger.info(f"Fixed %s", brain.getURL())

        if not self.request.form.get("write"):
            raise ValueError

        return "done"

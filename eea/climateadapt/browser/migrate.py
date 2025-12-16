from eea.climateadapt.interfaces import ICCACountry
from eea.climateadapt.interfaces import ICCACountry2025
from zope.interface import noLongerProvides
from zope.interface import alsoProvides

import logging
import csv
import io
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
from eea.climateadapt.translation.utils import get_site_languages

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
                logger.info("Progress %s of %s. Migrated %s",
                            idx, total, self.count)

        return self.count

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        count = self.migrate()
        IStatusMessage(self.request).addStatusMessage(
            "Migrated {} absolute URLs!".format(count)
        )
        return self.request.response.redirect(self.context.absolute_url())


class CountryMapInterface2025(BrowserView):
    """Migrate absolute URLs to resolveuid"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal_catalog = api.portal.get_tool("portal_catalog")
        languages = get_site_languages()
        for language in languages:
            logger.info(f"LANGUAGE %s", language)
            brains = portal_catalog.queryCatalog(
                {
                    "portal_type": "Folder",
                    "path": "/cca/{}/countries-regions/countries".format(language)
                }
            )
            for brain in brains:
                obj = brain.getObject()

                if ICCACountry.providedBy(obj):
                    noLongerProvides(obj, ICCACountry)
                    obj._p_changed = True

                if not ICCACountry2025.providedBy(obj):
                    alsoProvides(obj, ICCACountry2025)
                    obj._p_changed = True

                if obj._p_changed:
                    obj.reindexObject()
                    # transaction.commit()
                    logger.info(f"Interface update %s", brain.getURL())
        logger.info(f"Country profile interface check done")
        return 'done'


class ArchiveItems294148(BrowserView):
    """#294148 Research and Knowledge Projects and Reports and Publications"""

    def list(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal_catalog = api.portal.get_tool("portal_catalog")
        languages = get_site_languages()

        # import pdb
        # pdb.set_trace()
        response = []
        filterPortalTypes = []
        if self.request.form.get("publicationreport", None):
            filterPortalTypes.append('eea.climateadapt.publicationreport')
        if self.request.form.get("aceproject", None):
            filterPortalTypes.append('eea.climateadapt.aceproject')

        if len(filterPortalTypes) == 0:
            filterPortalTypes.append('eea.climateadapt.notypeselected')

        for language in languages:
            # if language not in ['en']:
            #     continue
            logger.info(f"ArchiveItems294148 LANGUAGE %s", language)
            brains = portal_catalog(**
                                    {
                                        "portal_type": filterPortalTypes,
                                        "review_state": "published",
                                        # "review_state": "archived",
                                        "path": "/cca/{}/".format(language)
                                    }
                                    )
            itemNr = 1
            nrToArchive = 0
            for brain in brains:
                obj = brain.getObject()
                yearCreated = brain.created.year() if getattr(brain, "created", None) else None
                yearPublication = obj.publication_date.year if obj.publication_date else None

                toArchive = 'N'
                if yearPublication and yearPublication < 2016:
                    nrToArchive += 1
                    toArchive = 'Y'
                # elif yearCreated and yearCreated < 2016:
                #     nrToArchive += 1
                #     toArchive = 'Y'

                # if toArchive and self.request.form.get("doarchive", None):
                #     import pdb
                #     pdb.set_trace()
                if toArchive == 'Y' and self.request.form.get("publicationreport", None) and self.request.form.get("doarchive", None):
                    api.content.transition(obj, "archive")
                    if nrToArchive % 100 == 0:
                        transaction.commit()
                response.append(
                    {
                        "itemNr": itemNr,
                        "nrToArchive": nrToArchive if toArchive == 'Y' else '',
                        "toArchive": toArchive,
                        "title": obj.title,
                        "url": brain.getURL(),
                        "created": yearCreated,
                        "publication_date": yearPublication,
                    }
                )
                itemNr += 1
        transaction.commit()
        logger.info(f"ArchiveItems294148 check done")
        return response


class ImpactFiltersNew:
    """New impact filters"""
    # migrate_262157_impact_filter

    def list(self):
        response = []
        fileUploaded = self.request.form.get("fileToUpload", None)

        if not fileUploaded:
            return response

        data = fileUploaded.read().decode('utf-8')
        csv_file = io.StringIO(data)
        reader = csv.DictReader(csv_file)

        i_transaction = 0
        count_found = 0
        count_not_found = 0
        for row in reader:
            i_transaction += 1
            if i_transaction % 100 == 0:
                transaction.savepoint()

            # print(row)
            # import pdb
            # pdb.set_trace()

            item = {}
            item["uid"] = row['UID']
            item["url"] = row['URL']
            item["title"] = row['Title']
            item["keywords"] = row['Keywords']
            item["sectors"] = row['Sectors']
            item["impacts"] = row['Impacts']
            item["elements"] = row['Elements']

            item["extreme_heat"] = row['EXTREME HEAT']
            item["extreme_cold"] = row['EXTREME COLD']
            item["wildfires"] = row['WILDFIRES']
            item["non_specific"] = row['NON SPECIFIC']

            obj = api.content.get(UID=item["uid"])

            if not obj:
                count_not_found += 1
                logger.info("NOT FOUND obj: %s", item['url'])
                continue
            count_found += 1

            # if '87d7dc67e16a4bc4b7320daf5ad670c9' == item['uid']:
            #     import pdb
            #     pdb.set_trace()

            changeMade = False
            if item['extreme_heat'] and 'EXTREMEHEAT' not in obj.climate_impacts:
                obj.climate_impacts.append('EXTREMEHEAT')
                changeMade = True
            if item['extreme_cold'] and 'EXTREMECOLD' not in obj.climate_impacts:
                obj.climate_impacts.append('EXTREMECOLD')
                changeMade = True
            if item['wildfires'] and 'WILDFIRES' not in obj.climate_impacts:
                obj.climate_impacts.append('WILDFIRES')
                changeMade = True
            if item['non_specific'] and 'NONSPECIFIC' not in obj.climate_impacts:
                obj.climate_impacts.append('NONSPECIFIC')
                changeMade = True

            if obj.climate_impacts and 'EXTREMETEMP' in obj.climate_impacts:
                obj.climate_impacts.remove('EXTREMETEMP')
                changeMade = True

            if changeMade:
                obj._p_changed = True

            response.append(
                {
                    "title": obj.title,
                    "url": item["url"],
                    "funding_programme": obj.title,
                }
            )
            logger.info("OBJ: %s",
                        obj.absolute_url())

        transaction.commit()

        logger.info("LINES IN RESPONSE: %s, FOUND %s, NOTFOUND %s",
                    len(response), count_found, count_not_found)
        return response


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

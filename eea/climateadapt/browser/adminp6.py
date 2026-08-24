import logging
import re

import transaction
from Acquisition import aq_inner, aq_parent
from plone.api.portal import get_tool
from plone.base.utils import base_hasattr, safe_callable
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

logger = logging.getLogger("eea.climateadapt")

CASE_STUDY_PORTAL_TYPE = "eea.climateadapt.casestudy"


class GoPDB(BrowserView):
    def __call__(self):
        import pdb

        pdb.set_trace()
        x = self.context.Creator()


class ReindexFolder(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        # Empties catalog, then finds all contentish objects (i.e. objects
        # with an indexObject method), and reindexes them.
        # This may take a long time.
        catalog = self.context.portal_catalog
        idxs = list(catalog.indexes())
        base_path = "/".join(self.context.getPhysicalPath())

        def indexObject(obj, path):
            if (
                obj != self
                and base_hasattr(obj, "reindexObject")
                and safe_callable(obj.reindexObject)
            ):
                try:
                    catalog.reindexObject(obj, idxs=idxs)
                    logger.info(f"Reindex {path}")
                    # index conversions from plone.app.discussion
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass
                except AttributeError:
                    logger.warning(f"Could not index {base_path}{path}")

        indexObject(self.context, "")
        portal = aq_parent(aq_inner(catalog))
        portal.ZopeFindAndApply(self.context, search_sub=True, apply_func=indexObject)


class ReindexContentType(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        catalog = self.context.portal_catalog
        ix = self.request.form.get("idxs", [])
        if ix:
            idxs = [ix]
        else:
            idxs = None

        ct = self.request.form.get("ct")

        brains = self.context.portal_catalog.searchResults(
            portal_type=ct, path="/".join(self.context.getPhysicalPath())
        )
        for brain in brains:
            obj = brain.getObject()
            catalog.reindexObject(obj, idxs=idxs)
            logger.info("Reindexed %s", obj.absolute_url())

        return "done"


class TriggerCaseStudiesModified(BrowserView):
    """Trigger ObjectModifiedEvent for case study items."""

    def get_language(self):
        language = self.request.form.get("language", "en").strip().lower()
        if not re.match(r"^[a-z]{2}$", language):
            raise ValueError("language must be a two-letter code")
        return language

    def get_language_path(self, language):
        portal = get_tool("portal_url").getPortalObject()
        portal_path = "/".join(portal.getPhysicalPath())
        return "{}/{}".format(portal_path, language)

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        language = self.get_language()
        catalog = self.context.portal_catalog
        path = self.get_language_path(language)
        brains = catalog.searchResults(
            portal_type=CASE_STUDY_PORTAL_TYPE,
            path=path,
        )

        total = len(brains)
        count = 0
        errors = 0
        try:
            batch_size = int(self.request.form.get("batch_size", 100))
        except (TypeError, ValueError):
            batch_size = 100
        batch_size = max(batch_size, 1)

        for idx, brain in enumerate(brains, start=1):
            try:
                obj = brain.getObject()
                modified(obj)
                count += 1
                logger.info("Triggered modified event for %s", brain.getURL())
            except Exception:
                errors += 1
                logger.exception(
                    "Could not trigger modified event for %s",
                    brain.getURL(),
                )

            if idx % batch_size == 0:
                transaction.commit()
                logger.info(
                    "Triggered modified event for %s/%s case study items",
                    idx,
                    total,
                )

        transaction.commit()
        return (
            "Triggered modified event for {} of {} case study items"
            " under {} for language {}. Errors: {}"
        ).format(count, total, path, language, errors)


class InspectCatalog(BrowserView):
    def __call__(self):
        catalog = get_tool("portal_catalog")
        path = "/".join(self.context.getPhysicalPath())

        try:
            rid = catalog._catalog.uids[path]
        except Exception:
            return f"{path} not found in catalog"

        url = f"{catalog.absolute_url()}/manage_objectInformation?rid={rid}"
        return self.request.response.redirect(url)

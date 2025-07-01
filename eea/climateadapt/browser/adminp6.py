import logging

from Acquisition import aq_inner, aq_parent
from plone.api.portal import get_tool
from plone.base.utils import base_hasattr, safe_callable
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides

logger = logging.getLogger("eea.climateadapt")


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

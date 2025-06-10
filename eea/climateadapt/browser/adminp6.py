from Products.Five.browser import BrowserView
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from plone.base.utils import base_hasattr
from plone.base.utils import safe_callable
from Acquisition import aq_inner
from Acquisition import aq_parent
import logging

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
        portal.ZopeFindAndApply(
            self.context, search_sub=True, apply_func=indexObject)

""" Transregional select dropdown
"""

from zope.component.hooks import getSite
from zope.interface import providedBy
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
# from eea.climateadapt.translation.utils import TranslationUtilsMixin


# TODO add TranslationUtilsMixin to inheritance
class TransRegionSelect(BrowserView):
    """ A dropdown select with transnational regions
    """

    def regions(self):
        site = getSite()

        catalog = getToolByName(site, 'portal_catalog')
        q = {
            "object_provides":
                "eea.climateadapt.interfaces.ITransnationalRegionMarker",
            'sort_on': 'getObjPositionInParent',
            'path': '/cca/'+self.current_lang
        }
        brains = catalog.searchResults(**q)

        results = []

        for b in brains:
            obj = b.getObject()
            if obj.title == 'Balkan-Mediterranean Area':
                continue
            provides = ["%s.%s" % (iface.__module__ or '', iface.__name__)
                        for iface in providedBy(obj)]

            if "eea.climateadapt.interfaces.ITransnationalRegionMarker" \
                    in provides:
                results.append(b)
        return [{'url': b.getURL(), 'title': b.Title} for b in results]

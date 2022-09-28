""" Transregional select dropdown
"""

from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements, providedBy
from Products.Five.browser import BrowserView

from eea.climateadapt import MessageFactory as _
from Products.CMFCore.utils import getToolByName
from eea.climateadapt.translation.utils import TranslationUtilsMixin

class TransRegionSelect(BrowserView, TranslationUtilsMixin):
    """ A dropdown select with transnational regions
    """

    def regions(self):
        site = getSite()

        catalog = getToolByName(site, 'portal_catalog')
        q = {
            "object_provides":
                "eea.climateadapt.interfaces.ITransnationalRegionMarker",
            'sort_on': 'sortable_title',
            'path': '/cca/'+self.current_lang
        }
        brains = catalog.searchResults(**q)

        results = []

        for b in brains:
            obj = b.getObject()
            provides = ["%s.%s" % (iface.__module__ or '', iface.__name__)
                        for iface in providedBy(obj)]

            if "eea.climateadapt.interfaces.ITransnationalRegionMarker" \
                    in provides:
                results.append(b)

        return sorted([{'url': b.getURL(), 'title': b.Title} for b in results],
                      key=lambda x: x['title'])

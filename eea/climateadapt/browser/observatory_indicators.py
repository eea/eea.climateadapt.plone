from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from eea.climateadapt.translation.utils import TranslationUtilsMixin
from eea.climateadapt.vocabulary import _origin_website

from Products.Five import BrowserView

import lxml.html
import logging
from plone.api.portal import get_tool

logger = logging.getLogger("eea.climateadapt")


class ObservatoryIndicators(BrowserView, TranslationUtilsMixin):

    def get_varaible_from_query(self, variable):
        request = self.request
        if 'PARENT_REQUEST' not in request:
            return None
        if variable not in request["PARENT_REQUEST"].form:
            return None
        return request["PARENT_REQUEST"].form[variable]

    def get_selected_origin_websites(self):
        return self.get_varaible_from_query("origin_website")

    def get_selected_search(self):
        return self.get_varaible_from_query("search")

    def get_origin_websites(self):
        return _origin_website

    def get_search_params(self):
        #import pdb; pdb.set_trace()
        search_params = {
                        "path": "/cca/"+self.current_lang,
                        "portal_type": ["eea.climateadapt.indicator","eea.climateadapt.c3sindicator"],
                        "include_in_observatory":"True",
                        "review_state": "published"
                    }
        selected_origin = self.get_selected_origin_websites()
        selected_search = self.get_selected_search()
        if selected_search:
            search_params['SearchableText'] = selected_search
        if selected_origin:
            search_params['origin_website'] = selected_origin
        return search_params

    def get_data(self):
        catalog = get_tool("portal_catalog")
        items = []
        health_impacts = {
            'Heat':{'value':0,'icon':'fa fa-area-chart'},
            'Droughts and floods':{'value':0,'icon':'fa fa-compass'},
            'Climate-sensitive diseases':{'value':0,'icon':'fa fa-info-circle'},
            'Air pollution and aero-allergens':{'value':0,'icon':'fa fa-file-video-o'},
            'Wildfires':{'value':0,'icon':'fa fa-wrench'}
        }

        search_params = self.get_search_params()
        #import pdb; pdb.set_trace()
        #if selected_origin:
        #    search_params = {}
        brains = catalog.searchResults(search_params)
        for brain in brains:
            obj = brain.getObject()
            origin_website = ''
            if hasattr(obj, "origin_website"):
                origin_website = ', '.join(obj.origin_website)
            for key in health_impacts:
                if key in obj.health_impacts:
                    health_impacts[key]['value']+=1
            items.append({
                    "title": obj.title,
                    "id": brain.UID,
                    "url": brain.getURL(),
                    "origin_websites": origin_website,
                    "health_impacts_tag": '_'+'_'.join(obj.health_impacts).lower().replace(' ','_')+'_',
                    "year": obj.publication_date.year
                })

        #import pdb; pdb.set_trace()
        return {'items':items,'health_impacts':health_impacts}

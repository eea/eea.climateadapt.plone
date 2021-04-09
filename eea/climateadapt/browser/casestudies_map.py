from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import json
from plone.api.portal import get_tool

class Items(BrowserView):

    def __call__(self):
        """"""
        factory = getUtility(IVocabularyFactory, 'eea.climateadapt.aceitems_climateimpacts')
        vocabulary_impacts = factory(self.context)
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary_sectors = factory(self.context)

        results = {
        	"type": "FeatureCollection",
        	"metadata": {
        		"generated": 1615559750000,
        		"url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson",
        		"title": "Cliamte-Adapta arcgis items",
        		"status": 200,
        		"api": "1.10.3",
        		"count": 10739
        	},
            "features": []
        }

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy",
                    "eea.climateadapt.adaptationoption",
                ]
            }
        )

        iPos = 0
        for brain in brains:
            obj = brain.getObject()
            if hasattr(obj, 'geolocation') and obj.geolocation:
                list_adaptation_options = []
                list_adaptation_options_links = []
                adaptation_options = obj.adaptationoptions
                for ao_related in adaptation_options:
                    try:
                        list_adaptation_options.append(ao_related.to_object.title)
                        list_adaptation_options_links.append('<a href=\''+ao_related.to_object.absolute_url_path()+'\'>'+ao_related.to_object.title+'</a>')
                    except:
                        ''

                sectors_str = [];
                impacts_str = [];
                for sector in obj.sectors:
                    try:
                        sectors_str.append(vocabulary_sectors.getTerm(sector).title)
                    except:
                        ''
                for impact in obj.climate_impacts:
                    try:
                        impacts_str.append(vocabulary_impacts.getTerm(impact).title)
                    except:
                        ''


                results['features'].append({
                        "properties": {
                            "portal_type":  obj.portal_type.replace('eea.climateadapt.', ''),
                            #"sectors": obj.sectors,
                            "sectors":  ','+(','.join(obj.sectors))+',',
                            "impacts": ','+(','.join(obj.climate_impacts))+',',
                            "adaptation_options": '<>'.join(list_adaptation_options),
                            "adaptation_options_links": '<>'.join(list_adaptation_options_links),

                            "sectors_str": ','.join(sectors_str),
                            "impacts_str": ','.join(impacts_str),
                            "title": obj.title,
                            "description": brain.long_description.raw,
                            "url": brain.getURL(),
                            "image": brain.getURL()+'/@@images/primary_photo/mini' if obj.primary_photo else ''
                        },
                        "geometry": {
                            "type": "Point",
                            #"coordinates": [geo.x, geo.y]
                            "coordinates": [obj.geolocation.longitude, obj.geolocation.latitude]
                        }
                    })
                iPos = iPos + 1

        response = self.request.response
        response.setHeader('Content-type', 'application/json')

        return json.dumps(results)

class Page(BrowserView):

    def get_climate_impacts(self):
        factory = getUtility(IVocabularyFactory, 'eea.climateadapt.aceitems_climateimpacts')
        vocabulary = factory(self.context)
        response = [];
        response.append({"key": "", "value": "Filter by IMPACT"})
        for term in vocabulary:
            response.append({"key": term.value, "value": term.title})
        return response

    def get_sectors(self):
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary = factory(self.context)
        response = [];
        response.append({"key": "", "value": "Filter by SECTOR"})
        for term in vocabulary:
            response.append({"key": term.value, "value": term.title})
        return response

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import json
from plone.api.portal import get_tool

class Items(BrowserView):

    def __call__(self):
        """"""
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
            #import pdb; pdb.set_trace()
            if hasattr(obj, 'geolocation') and obj.geolocation:
                #import pdb; pdb.set_trace()
                list_adaptation_options = []
                adaptation_options = obj.adaptationoptions
                for ao_related in adaptation_options:
                    #import pdb; pdb.set_trace()
                    try:
                        list_adaptation_options.append(ao_related.to_object.title)
                    except:
                        ''

                #import pdb; pdb.set_trace()
                results['features'].append({
                        "properties": {
                            "portal_type":  obj.portal_type.replace('eea.climateadapt.', ''),
                            #"sectors": obj.sectors,
                            "sectors":  ','.join(obj.sectors),
                            "impacts": ','.join(obj.climate_impacts),
                            "adaptation_options": '<>'.join(list_adaptation_options),

                            "sectors_str": ','.join(obj.sectors),
                            "impacts_str": ','.join(obj.climate_impacts),
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

    def __call__(self):
        """"""

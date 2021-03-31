from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from eea.climateadapt.sat.utils import _measure_id, to_arcgis_coords

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
                geo = to_arcgis_coords(
                    obj.geolocation.latitude, obj.geolocation.longitude
                )
                #import pdb; pdb.set_trace()
                results['features'].append({
                        "properties": {
                            "portal_type":  obj.portal_type.replace('eea.climateadapt.', '') if iPos % 10 <2 else 'adaptationoption',
                            #"sectors": obj.sectors,
                            "sectors": ',' + ','.join(obj.sectors) + ',',
                            "impacts": ',' + ','.join(obj.climate_impacts) + ',',
                            "title": obj.title,
                            "url": brain.getURL()
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

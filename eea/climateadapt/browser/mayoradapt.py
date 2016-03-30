# coding=utf-8
import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView
import json

from eea.climateadapt.vocabulary import _sectors
from eea.climateadapt.vocabulary import _stage_implementation_cycle
from eea.climateadapt.vocabulary import _climateimpacts
from eea.climateadapt.vocabulary import ace_countries

class IMAdaptView (Interface):
    """ Countries Interface """


class MAdaptView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/mayors-adapt """

    implements(IMAdaptView)


class b_m_climate_impacts (BrowserView):
    def __call__(self):
        return json.dumps(_climateimpacts)


class a_m_country (BrowserView):
    def __call__(self):
        return json.dumps(ace_countries)


class b_m_sector (BrowserView):
    def __call__(self):
        return json.dumps(_sectors)


class c_m_stage_of_the_implementation_cycle (BrowserView):
    def __call__(self):
        return json.dumps(_stage_implementation_cycle)


class citiesxyz (BrowserView):
    def __call__(self):
        cat = self.context.portal_catalog
        q = {
            'portal_type': 'eea.climateadapt.city_profile'
        }
        for k, v in self.request.form.items():
            v = v and v.strip() or None
            if v:
                q[k] = v
        brains = cat.searchResults(**q)
        res = {}
        for brain in brains:
            res[brain.Title] = brain.getURL()

        return json.dumps(res)

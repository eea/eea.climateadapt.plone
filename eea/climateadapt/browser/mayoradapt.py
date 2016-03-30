# coding=utf-8

from Products.Five.browser import BrowserView
from eea.climateadapt.vocabulary import _climateimpacts
from eea.climateadapt.vocabulary import _sectors
from eea.climateadapt.vocabulary import _stage_implementation_cycle
from eea.climateadapt.vocabulary import ace_countries
from zope.interface import Interface
from zope.interface import implements
import json


class IMAdaptView (Interface):
    """ Countries Interface """


class MayorsAdaptPage (BrowserView):
    """ Custom page for http://climate-adapt.eea.europa.eu/mayors-adapt """

    implements(IMAdaptView)


class B_M_Climate_Impacts (BrowserView):
    def __call__(self):
        return json.dumps(_climateimpacts)


class A_M_Country (BrowserView):
    def __call__(self):
        return json.dumps(ace_countries)


class B_M_Sector (BrowserView):
    def __call__(self):
        return json.dumps(_sectors)


class C_M_Stage_Of_The_Implementation_Cycle (BrowserView):
    def __call__(self):
        return json.dumps(_stage_implementation_cycle)


class CitiesLoad (BrowserView):
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

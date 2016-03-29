# coding=utf-8
import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView
import json

class IMAdaptView (Interface):
    """ Countries Interface """


class MAdaptView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/mayors-adapt """

    implements(IMAdaptView)


class b_m_climate_impacts (BrowserView):
    def __call__(self):
        _climateimpacts = [
            ("FORESTFIRES", "Forest Fires"),
            ("EXTREMETEMP", "Extreme Temperatures"),
            ("WATERSCARCE", "Water Scarcity"),
            ("FLOODING", "Flooding"),
            ("SEALEVELRISE", "Sea Level Rise"),
            ("DROUGHT", "Droughts"),
            ("STORM", "Storms"),
            ("ICEANDSNOW", "Ice and Snow"),
            ]

        return json.dumps(_climateimpacts)


class a_m_country (BrowserView):
    def __call__(self):
        _countries = [
            ("Albania", "Albania"), ("Austria", "Austria"), ("Belgium", "Belgium"),
            ("Bulgaria", "Bulgaria"), ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
            ("Croatia", "Croatia"), ("Cyprus", "Cyprus"), ("Czech Republic", "Czech Republic"),
            ("Denmark", "Denmark"), ("Estonia", "Estonia"), ("Finland", "Finland"),
            ("Former Yugoslav Republic of Macedonia", "Former Yugoslav Republic of Macedonia"),
            ("France", "France"), ("Germany", "Germany"), ("Greece", "Greece"),
            ("Hungary", "Hungary"), ("Iceland", "Iceland"), ("Ireland", "Ireland"),
            ("Italy", "Italy"),
            ("Kosovo under UN Security Council Resolution 124", "Kosovo under UN Security Council Resolution 124"),
            ("Latvia", "Latvia"), ("Liechtenstein", "Liechtenstein"),
            ("Lithuania", "Lithuania"), ("Luxembourg", "Luxembourg"), ("Malta", "Malta"),
            ("Montenegro", "Montenegro"), ("Netherlands", "Netherlands"),
            ("Norway", "Norway"), ("Poland", "Poland"), ("Portugal", "Portugal"),
            ("Romania", "Romania"), ("Serbia", "Serbia"), ("Slovakia", "Slovakia"),
            ("Slovenia", "Slovenia"), ("Spain", "Spain"), ("Sweden", "Sweden"),
            ("Switzerland", "Switzerland"), ("Turkey", "Turkey"), ("United Kingdom", "United Kingdom"),
                     ]

        return json.dumps(_countries)
        # return """["Albania","Austria","Belgium","Bulgaria","Bosnia and Herzegovina","Croatia","Cyprus","Czech Republic","Denmark","Estonia","Finland","Former Yugoslav Republic of Macedonia","France","Germany","Greece","Hungary","Iceland","Ireland","Italy","Kosovo under UN Security Council Resolution 124","Latvia","Liechtenstein","Lithuania","Luxembourg","Malta","Montenegro","Netherlands","Norway","Poland","Portugal","Romania","Serbia","Slovakia","Slovenia","Spain","Sweden","Switzerland","Turkey","United Kingdom"]"""


class b_m_sector (BrowserView):
    def __call__(self):
        _key_vulnerable_adapt_sector = [
            ("AGRI_AND_FOREST", "Agriculture and Forest"),
            ("COASTAL_AREAS", "Coastal areas"),
            ("DISASTER_RISK", "Disaster Risk Reduction"),
            ("FINANCIAL", "Financial"),
            ("HEALTH", "Health"),
            ("INFRASTRUCTURE", "Infrastructure"),
            ("MARINE_AND_FISH", "Marine and Fisheries"),
            ("TOURISM", "Tourism"),
            ("ENERGY", "Energy"),
            ("OTHER", "Other"),
            ("BIODIVERSITY", "Biodiversity"),
            ("WATER_MANAGEMENT", "Water Management"),
            ("URBAN", "Urban"),
            ]
        # import pdb; pdb.set_trace()
        return json.dumps(_key_vulnerable_adapt_sector)


class c_m_stage_of_the_implementation_cycle (BrowserView):
    def __call__(self):

        _stage_implementation_cycle = [
            ("", "Select"),
            ("PREPARING_GROUND", "Preparing the ground"),
            ("ASSESSING_RISKS_VULNER", "Assessing risks and vulnerabilities"),
            ("IDENTIF_ADAPT_OPT", "Identifying adaptation options"),
            ("ASSESSING_ADAPT_OPT", "Assessing adaptation options"),
            ("IMPLEMENTATION", "Implementation"),
            ("MONIT_AND_EVAL", "Monitoring and evaluation"),
            ]

        return json.dumps(_stage_implementation_cycle)


class citiesxyz (BrowserView):
    def __call__(self):
        # read parameters from request
        # search in portal_catalog for CityProfiles of those parameters from request
        # make the json String
        # return json string

#        requested = self.request.form
#        requested['title']
#        self.context.portal_catalog.searchResults(Title='Romania')
#        zz = self.context.portal_catalog.searchResults(Title='Romania')[0]
#        zz.getObject()
#        self.context.portal_catalog.searchResults(Title='Romania')[1].getObject()
#        pp [o.getObject() for o in self.context.portal_catalog.searchResults(Title='Romania', portal_type='Folder')]

#        import json
#        objs = [c1, c2]
#        res = {}
#        for obj in res:
#            res[obj.id] = obj.absolute_url()

#        return json.dumps(res)

        cat = self.context.portal_catalog
        q = {
            'portal_type': 'eea.climateadapt.city_profile'
        }
        for k, v in self.request.form.items():
            q[k] = v

        brains = cat.searchResults(**q)
        res = {}
        for brain in brains:
            res[brain.Title] = brain.getURL()

        return json.dumps(res)

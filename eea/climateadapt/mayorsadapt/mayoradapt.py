# coding=utf-8
from Products.Five.browser import BrowserView
from eea.climateadapt.city_profile import MAIL_TEXT_TEMPLATE
from eea.climateadapt.mayorsadapt.vocabulary import _climateimpacts
from eea.climateadapt.mayorsadapt.vocabulary import _sectors
from eea.climateadapt.mayorsadapt.vocabulary import _stage_implementation_cycle
from eea.climateadapt.vocabulary import ace_countries
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.interface import implements
import json
import tokenlib


class ITokenMailView(Interface):
    """Token mail interface"""


class TokenMailView (BrowserView):
    implements(ITokenMailView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        city = self.context
        tokensecret = IAnnotations(city)['eea.climateadapt.cityprofile_secret']
        # 4 weeks = 2419200
        self.secret = tokenlib.make_token({"": ""}, secret=tokensecret,
                                          timeout=2419200)
        try:
            self.emailto = str(city.official_email)
        except:
            # TODO: debug this
            self.emailto = ""
        self.receivername = city.name_and_surname_of_contact_person
        self.cityurl = city.virtual_url_path().encode(encoding='UTF-8')
        self.city_full_url = self.context.portal_url() + \
            '/cptk/' + self.secret + '/' + self.cityurl
        self.text_plain_dictionary = {'receivername': self.receivername,
                                      'cityurl':  self.city_full_url}
        self.MAIL_TEXT_TEMPLATE = MAIL_TEXT_TEMPLATE % \
            (self.text_plain_dictionary)

    def html(self):
        return self.index()


class IMAdaptView(Interface):
    """ Mayors Adapt Interface """


class MayorsAdaptPage(BrowserView):
    """ Custom page for http://climate-adapt.eea.europa.eu/mayors-adapt """

    implements(IMAdaptView)


class B_M_Climate_Impacts(BrowserView):
    def __call__(self):
        return json.dumps(_climateimpacts)


class A_M_Country(BrowserView):
    def __call__(self):
        return json.dumps(ace_countries)


class B_M_Sector(BrowserView):
    def __call__(self):
        return json.dumps(_sectors)


class C_M_Stage_Of_The_Implementation_Cycle(BrowserView):
    def __call__(self):
        return json.dumps(_stage_implementation_cycle)


class CitiesLoad(BrowserView):
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

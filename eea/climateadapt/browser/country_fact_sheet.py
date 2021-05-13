import json
import logging
import urllib2

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.climateadapt.vocabulary import ace_countries
from plone.intelligenttext.transforms import \
    convertWebIntelligentPlainTextToHtml as convWebInt

from datetime import datetime

logger = logging.getLogger("eea.climateadapt")


DISCODATA_URL = 'https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_JSON%5D&p=1&nrOfHits=100'


class CountryProfileData(BrowserView):
    template = ViewPageTemplateFile("pt/country-profile.pt")

    @property
    def annotations(self):
        return self.context.__annotations__

    def convert_web_int(self, text):
        return convWebInt(text)

    def get_sorted_affected_sectors_data(self):
        items = self.processed_data['National_Circumstances'].get(
            'Afected_Sectors', [])

        sorted_items = sorted(
            items,
            key=lambda i: (i['SectorTitle'], i['SectorDescribeIfOther'])
        )

        return sorted_items

    def get_sorted_action_measures_data(self):
        items = self.processed_data['Strategies_Plans'].get(
            'Action_Measures', [])

        sorted_items = sorted(
            items,
            key=lambda i: (i['KeyTypeMeasure'], i['subKTM'], i['Title'])
        )

        return sorted_items

    def get_sorted_available_practices_data(self):
        items = self.processed_data['Cooperation_Experience'].get(
            'Available_Good_Practices', [])

        sorted_items = sorted(
            items,
            key=lambda i: i['Area']
        )

        return sorted_items

    def get_data(self):
        if 'discodata' not in self.annotations:
            return self.setup_data()

        last_import_date = self.annotations['discodata']['timestamp']

        if (datetime.now() - last_import_date).total_seconds() > 60*2:
            return self.setup_data()

        return self.annotations['discodata']['data']

    def setup_data(self):
        response = urllib2.urlopen(DISCODATA_URL)
        data = json.loads(response.read())
        self.annotations['discodata'] = {
                'timestamp': datetime.now(),
                'data': data
            }
        logger.info("RELOAD URL %s", DISCODATA_URL)

        return data

    def __call__(self):
        country_name = self.context.title
        country_code = next(
            (k for k, v in ace_countries if v == country_name), 'Not found'
        )

        data = self.get_data()
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']
        orig_data = next((
            x
            for x in data['results']
            if x['countryCode'] == country_code
        ), {})

        # remove the countryCode as we don't need it
        processed_data = {
            k: unicode(v)
            for k, v in orig_data.items()
            if k != 'countryCode'
        }

        # some values are strings, and need to be transformed
        # into Python objects
        for k, val in processed_data.items():
            json_val = json.loads(val)
            new_value = json_val[k][0]

            processed_data[k] = new_value

        self.processed_data = processed_data

        return self.template(country_data=processed_data,
                             original_data=orig_data)


class CountryProfileDataRaw(CountryProfileData):
    template = ViewPageTemplateFile("pt/country-profile-raw.pt")

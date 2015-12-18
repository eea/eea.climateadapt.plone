import json

#
labels = """
acesearch-geochars-lbl-GLOBAL=Global
acesearch-geochars-lbl-EUROPE=Europe
acesearch-geochars-lbl-MACRO_TRANSNATIONAL_REGION=Macro-Transnational Regions
acesearch-geochars-lbl-BIOGRAPHICAL_REGION=Biogeographical Regions
acesearch-geochars-lbl-COUNTRIES=Countries
acesearch-geochars-lbl-SUBNATIONAL=Subnational Regions
acesearch-geochars-lbl-CITY=Municipality Name
acesearch-geochars-lbl-TRANS_MACRO_NORTHPERI=Northern Periphery
acesearch-geochars-lbl-TRANS_MACRO_BACLITC=Baltic Sea
acesearch-geochars-lbl-TRANS_MACRO_NW_EUROPE=North West Europe
acesearch-geochars-lbl-TRANS_MACRO_N_SEA=North Sea
acesearch-geochars-lbl-TRANS_MACRO_ATL_AREA=Atlantic Area
acesearch-geochars-lbl-TRANS_MACRO_ALP_SPACE=Alpine Space
acesearch-geochars-lbl-TRANS_MACRO_CEN_EUR=Central Europe
acesearch-geochars-lbl-TRANS_MACRO_SW_EUR=South West Europe
acesearch-geochars-lbl-TRANS_MACRO_MED=Mediterranean
acesearch-geochars-lbl-TRANS_MACRO_SE_EUR=South East Europe
acesearch-geochars-lbl-TRANS_MACRO_CAR_AREA=Caribbean Area
acesearch-geochars-lbl-TRANS_MACRO_MACRONESIA=Macronesia
acesearch-geochars-lbl-TRANS_MACRO_IND_OCEAN_AREA=Indian Ocean Area
acesearch-geochars-lbl-TRANS_BIO_ALPINE=Alpine
acesearch-geochars-lbl-TRANS_BIO_ATLANTIC=Atlantic
acesearch-geochars-lbl-TRANS_BIO_ARCTIC=Arctic
acesearch-geochars-lbl-TRANS_BIO_CONTINENTAL=Continental
acesearch-geochars-lbl-TRANS_BIO_MEDIT=Mediterranean
acesearch-geochars-lbl-TRANS_BIO_PANONIAN=Panonian
"""

TRANSLATED = {}

for line in filter(None, labels.split('\n')):
    first, label = line.split('=')
    name = first.split('-lbl-')[1]
    TRANSLATED[name] = label


class AceViewApi(object):

    def _render_geochar_element(self, value):
        return TRANSLATED[value] + u": <br/>"

    def _render_geochar_macrotrans(self, value):
        return u"Macro-Transnational region: " + u", ".join(
            [TRANSLATED[x] for x in value])

    def _render_geochar_biotrans(self, value):
        return u" ".join(TRANSLATED.get(x, u'') for x in value)

    def _render_geochar_countries(self, value):
        return (u"Countries:<br/><ul><li>" +
                u"</li><li>".join(value) +
                "</li></ul>")

    def _render_geochar_subnational(self, value):
        return u" ".join(TRANSLATED.get(x, u'') for x in value)

    def _render_geochar_city(self, value):
        return u" ".join(TRANSLATED.get(x, u'') for x in value)

    def render_geochar(self, value):
        # value is a mapping such as:
        # u'{"geoElements":{"element":"EUROPE",
        #                   "macrotrans":["TRANS_MACRO_ALP_SPACE"],
        #                   "biotrans":[],
        #                   "countries":[],
        #                   "subnational":[],
        #                   "city":""}}'

        value = json.loads(value)

        out = []
        order = ['element', 'macrotrans', 'biotrans',
                 'countries', 'subnational', 'city']

        for key in order:
            element = value['geoElements'].get(key)
            renderer = getattr(self, "_render_geochar_" + key)
            if element:
                out.append(renderer(element))

        return u" ".join(out)

    def link_to_original(self):
        """ Returns link to original object, to allow easy comparison
        """

        raise NotImplementedError

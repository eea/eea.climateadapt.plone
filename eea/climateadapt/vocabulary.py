# -*- coding: utf-8 -*-

from collections import namedtuple

import pycountry
from plone.app.querystring import queryparser
from plone.app.vocabularies.catalog import CatalogVocabulary as BCV
from plone.app.vocabularies.catalog import CatalogVocabularyFactory
from plone.app.vocabularies.catalog import KeywordsVocabulary as BKV
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import alsoProvides, implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from eea.climateadapt import MessageFactory as _


def generic_vocabulary(_terms, sort=True):
    """Returns a zope vocabulary from a dict or a list"""

    if _terms and isinstance(_terms, dict):
        _terms = list(_terms.items())
    elif _terms and isinstance(_terms[0], str):
        _terms = [(x, x) for x in _terms]

    if sort:
        _terms = sorted(_terms, key=lambda x: x[0])

    def factory(context):
        terms = []
        for _term in _terms:
            value, title = _term
            # token = value.decode("utf-8").encode("utf-8", "replace")
            token = value
            term = SimpleTerm(value=value, token=token, title=title)
            terms.append(term)

        return SimpleVocabulary(terms)

    return factory


@implementer(IVocabularyFactory)
class KeywordsVocabulary(BKV):
    def __init__(self, index):
        self.keyword_index = index

    def __call__(self, context):
        vocab = super().__call__(context)
        terms = []
        for term in vocab:
            term_value = term.value
            terms.append(term.__class__(term_value, term_value, term_value))
        return vocab.__class__(terms)


class CatalogVocabulary(BCV):
    def getTerm(self, value):
        if isinstance(value, str):
            # perhaps it's already a uid
            uid = value
        else:
            uid = IUUID(value)

        for term in self._terms:
            try:
                term_uid = term.value.UID
            except AttributeError:
                term_uid = term.value

            if uid == term_uid:
                return term


@implementer(IVocabularyFactory)
class AdaptationOptionsVocabulary(CatalogVocabularyFactory):
    def __call__(self, context, query=None):
        query = query or {}

        if "criteria" not in query:
            query["criteria"] = []

        query["criteria"].append(
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["eea.climateadapt.adaptationoption"],
            }
        )

        parsed = {}

        if query:
            parsed = queryparser.parseFormquery(context, query["criteria"])

            if "sort_on" in query:
                parsed["sort_on"] = query["sort_on"]

            if "sort_order" in query:
                parsed["sort_order"] = str(query["sort_order"])
        try:
            catalog = getToolByName(context, "portal_catalog")
        except AttributeError:
            catalog = getToolByName(getSite(), "portal_catalog")

        if parsed.get("path"):
            if parsed["path"].get("depth"):
                parsed["path"]["query"].append(
                    "/cca/metadata/adaptation-options")

                if "/cca" in parsed["path"]["query"]:
                    parsed["path"]["query"].remove("/cca")

        brains = catalog(**parsed)

        return CatalogVocabulary.fromItems(brains, context)


@implementer(IVocabularyFactory)
class CaseStudiesVocabulary(CatalogVocabularyFactory):
    def __call__(self, context, query=None):
        query = query or {}

        if "criteria" not in query:
            query["criteria"] = []

        query["criteria"].append(
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["eea.climateadapt.casestudy"],
            }
        )

        parsed = {}

        if query:
            parsed = queryparser.parseFormquery(context, query["criteria"])

            if "sort_on" in query:
                parsed["sort_on"] = query["sort_on"]

            if "sort_order" in query:
                parsed["sort_order"] = str(query["sort_order"])
        try:
            catalog = getToolByName(context, "portal_catalog")
        except AttributeError:
            catalog = getToolByName(getSite(), "portal_catalog")

        if parsed.get("path"):
            if parsed["path"].get("depth"):
                parsed["path"]["query"].append("/cca/metadata/case-studies")

                if "/cca" in parsed["path"]["query"]:
                    parsed["path"]["query"].remove("/cca")

        brains = catalog(**parsed)

        return CatalogVocabulary.fromItems(brains, context)


@implementer(IVocabularyFactory)
class OrganisationsVocabulary(CatalogVocabularyFactory):
    def __call__(self, context, query=None):
        query = query or {}

        if "criteria" not in query:
            query["criteria"] = []

        query["criteria"].append(
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["eea.climateadapt.organisation"],
            }
        )
        query["criteria"].append(
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["published"],
            }
        )

        parsed = {}

        if query:
            parsed = queryparser.parseFormquery(context, query["criteria"])

            if "sort_on" in query:
                parsed["sort_on"] = query["sort_on"]

            if "sort_order" in query:
                parsed["sort_order"] = str(query["sort_order"])
        try:
            catalog = getToolByName(context, "portal_catalog")
        except AttributeError:
            catalog = getToolByName(getSite(), "portal_catalog")

        if parsed.get("path"):
            if parsed["path"].get("depth"):
                parsed["path"]["query"].append("/cca/metadata/organisations")

                if "/cca" in parsed["path"]["query"]:
                    parsed["path"]["query"].remove("/cca")

        brains = catalog(**parsed)

        return CatalogVocabulary.fromItems(brains, context)


@implementer(IVocabularyFactory)
class CCAItemsVocabulary(CatalogVocabularyFactory):
    def __call__(self, context, query=None):
        query = query or {}

        if "criteria" not in query:
            query["criteria"] = []

        query["criteria"].append(
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": [
                    "eea.climateadapt.adaptationoption",
                    "eea.climateadapt.aceproject",
                    "eea.climateadapt.casestudy",
                    "eea.climateadapt.guidancedocument",
                    "eea.climateadapt.indicator",
                    "eea.climateadapt.informationportal",
                    "eea.climateadapt.mapgraphdataset",
                    "eea.climateadapt.organisation",
                    "eea.climateadapt.publicationreport",
                    "eea.climateadapt.researchproject",
                    "eea.climateadapt.tool",
                    "Folder",
                ],
            }
        )

        parsed = {}

        if query:
            parsed = queryparser.parseFormquery(context, query["criteria"])

            if "sort_on" in query:
                parsed["sort_on"] = query["sort_on"]

            if "sort_order" in query:
                parsed["sort_order"] = str(query["sort_order"])
        try:
            catalog = getToolByName(context, "portal_catalog")
        except AttributeError:
            catalog = getToolByName(getSite(), "portal_catalog")

        if parsed.get("path"):
            if parsed["path"].get("depth"):
                parsed["path"]["query"].append("/cca/metadata")

                if "/cca" in parsed["path"]["query"]:
                    parsed["path"]["query"].remove("/cca")
        brains = catalog(**parsed)

        return CatalogVocabulary.fromItems(brains, context)


# changes title and buttons (what to add) in view for AceItem
# extracted from JAVA code:
_datatypes = [
    ("DOCUMENT", _("Publications and reports")),
    ("INFORMATIONSOURCE", _("Information portals")),
    ("MAPGRAPHDATASET", _("Maps, graphs and datasets")),
    ("INDICATOR", _("Indicators")),
    ("GUIDANCE", _("Guidance")),
    ("TOOL", _("Tools")),
    ("RESEARCHPROJECT", _("Research and knowledge projects")),
    ("MEASURE", _("Adaptation options")),
    ("ACTION", _("Case studies")),
    ("ORGANISATION", _("Organisations")),
    # ("VIDEOS", "Videos"),
]

aceitem_datatypes_vocabulary = generic_vocabulary(_datatypes)
alsoProvides(aceitem_datatypes_vocabulary, IVocabularyFactory)


# changes how the view for AceItem behaves (what it shows)
_storagetypes = [
    "PLAINMETADATA",
    "PROJECT",
    "MAPLAYER",
    "URL",
    "SETOFMAPS",
    "MEASURE",
]
aceitem_storagetypes_vocabulary = generic_vocabulary(_storagetypes)
alsoProvides(aceitem_storagetypes_vocabulary, IVocabularyFactory)


_sectors = [  # this is the canonical
    #   ("OTHER", "Other"),
    #   ("TOURISM", "Tourism"),
    # ("AGRICULTURE", "Agriculture and Forest"),
    # ("INFRASTRUCTURE", "Infrastructure"),
    # ("ECOSYSTEM", _("Ecosystem-based approaches (GI)")),
    ("AGRICULTURE", _("Agriculture")),
    ("BIODIVERSITY", _("Biodiversity protection")),
    ("BUILDINGS", _("Buildings")),
    ("BUSINESSINDUSTRY", _("Business and industry")),
    ("COASTAL", _("Coastal areas")),
    ("CULTURALHERITAGE", _("Cultural heritage")),
    ("DISASTERRISKREDUCTION", _("Disaster Risk Reduction")),
    ("ECOSYSTEMSRESTORATION", _("Ecosystems restoration")),
    ("ENERGY", _("Energy")),
    ("FINANCIAL", _("Financial")),
    ("FORESTRY", _("Forestry")),
    ("HEALTH", _("Health")),
    ("ICT", _("ICT")),
    ("LANDUSE", _("Land use planning")),
    ("MARINE", _("Marine and Fisheries")),
    ("MOUNTAINAREAS", _("Mountain areas")),
    ("TOURISMSECTOR", _("Tourism")),
    ("TRANSPORT", _("Transport")),
    ("URBAN", _("Urban")),
    ("WATERMANAGEMENT", _("Water management")),
    ("NONSPECIFIC", _("Non specific")),
]

aceitem_sectors_vocabulary = generic_vocabulary(_sectors, sort=False)
alsoProvides(aceitem_sectors_vocabulary, IVocabularyFactory)

_elements = [
    ("EU_POLICY", _("Sector Policies")),
    ("MEASUREACTION", _("Adaptation Measures and Actions")),
    ("OBSERVATIONS", _("Observations and Scenarios")),
    ("PLANSTRATEGY", _("Adaptation Plans and Strategies")),
    ("VULNERABILITY", _("Vulnerability Assessment")),
    ("CLIMATESERVICES", _("Climate services")),
    ("JUSTRESILIENCE", "Just Resilience"),
    ("MRE", "MRE"),
    ("NATUREBASEDSOL", _("Nature-based solutions")),
]
aceitem_elements_vocabulary = generic_vocabulary(_elements)
alsoProvides(aceitem_elements_vocabulary, IVocabularyFactory)

# 261447 - only for case studies we need 6 more elements
_elements_case_study = [
    ("EU_POLICY", _("Sector Policies")),
    ("MEASUREACTION", _("Adaptation Measures and Actions")),
    ("OBSERVATIONS", _("Observations and Scenarios")),
    ("PLANSTRATEGY", _("Adaptation Plans and Strategies")),
    ("VULNERABILITY", _("Vulnerability Assessment")),
    ("CLIMATESERVICES", _("Climate services")),
    ("JUSTRESILIENCE", "Just Resilience"),
    ("MRE", "MRE"),
    ("NATUREBASEDSOL", _("Nature-based solutions")),
    ("ENVIRONMENTALASP", _("Environmental aspects")),
    ("MITIGATIONASP", _("Mitigation aspects")),
    ("SOCIETALASP", _("Societal aspects")),
    ("ECONOMICASP", _("Economic aspects")),
    ("COSTBENEFIT", _("Cost-benefit analysis and maintenance costs")),
    ("RUPOTENTIAL", _("Replication/upscaling potential")),
]
aceitem_elements_case_study_vocabulary = generic_vocabulary(
    _elements_case_study)
alsoProvides(aceitem_elements_case_study_vocabulary, IVocabularyFactory)

# Vocabulary for faceted search "Adaptation elements"
fac_elements = [
    ("OBSERVATIONS", _("Observations and Scenarios")),
    ("VULNERABILITY", _("Vulnerability Assessment")),
    ("MEASUREACTION", _("Adaptation Measures and Actions")),
    ("PLANSTRATEGY", _("Adaptation Plans and Strategies")),
    ("EU_POLICY", _("Sector Policies")),
]
faceted_elements = generic_vocabulary(fac_elements, sort=False)
alsoProvides(faceted_elements, IVocabularyFactory)

_climateimpacts = [
    ("DROUGHT", _("Droughts")),
    # ("EXTREMETEMP", _("Extreme Temperatures")),
    ("EXTREMEHEAT", _("Extreme heat")),
    ("EXTREMECOLD", _("Extreme cold")),
    ("FLOODING", _("Flooding")),
    ("ICEANDSNOW", _("Ice and Snow")),
    ("SEALEVELRISE", _("Sea Level Rise")),
    ("STORM", _("Storms")),
    ("WATERSCARCE", _("Water Scarcity")),
    ("WILDFIRES", _("Wildfires")),
    ("NONSPECIFIC", _("Non specific")),
]
aceitem_climateimpacts_vocabulary = generic_vocabulary(
    _climateimpacts, sort=False)
alsoProvides(aceitem_climateimpacts_vocabulary, IVocabularyFactory)


_featured = [
    ("CASEHOME", "Feature this on the homepage"),
    ("CASESEARCH", "Feature this on study search results page"),
]
aceitem_featured_vocabulary = generic_vocabulary(_featured)
alsoProvides(aceitem_featured_vocabulary, IVocabularyFactory)

_relevance = [
    (
        "IMPL_AS_CCA",
        _("Case developed and implemented as a climate change adaptation measure."),
    ),
    (
        "PARTFUND_AS_CCA",
        _(
            "Case partially developed, implemented and funded as a climate change adaptation measure."
        ),
    ),
    (
        "OTHER_POL_OBJ",
        _(
            "Case mainly developed and implemented because of other policy objectives, but with significant consideration of climate change adaptation aspects."
        ),
    ),
]
aceitem_relevance_vocabulary = generic_vocabulary(_relevance, False)
alsoProvides(aceitem_relevance_vocabulary, IVocabularyFactory)

_implementationtypes = (
    ("grey", "Technical ('grey')"),
    ("green", "Ecological ('green')"),
    ("soft", "Behavioural / policy ('soft')"),
)
acemeasure_implementationtype_vocabulary = generic_vocabulary(
    _implementationtypes)
alsoProvides(acemeasure_implementationtype_vocabulary, IVocabularyFactory)

# Used for aceitems
european_countries = [
    "AD",
    "AL",
    "AM",
    "AT",
    "AZ",
    "BA",
    "BE",
    "BG",
    "BY",
    "CH",
    "RS",
    "CY",
    "CZ",
    "DE",
    "DK",
    "EE",
    "ES",
    "FI",
    "FO",
    "FR",
    "GB",
    "GE",
    "GR",
    "HR",
    "HU",
    "IE",
    "IL",
    "IS",
    "IT",
    "KZ",
    "LI",
    "LT",
    "LU",
    "LV",
    "MC",
    "MD",
    "MT",
    "NL",
    "NO",
    "PL",
    "PT",
    "RO",
    "RU",
    "SE",
    "SI",
    "SK",
    "SM",
    "TR",
    "UA",
    "ME",
]
ace_countries = [
    (x.alpha_2, x.name) for x in pycountry.countries if x.alpha_2 in european_countries
]
ace_countries = [x for x in ace_countries if x[0] != "CZ"]
ace_countries.append((str("CZ"), "Czechia"))
ace_countries = sorted(ace_countries, key=lambda x: x[0])
# ace_countries.append(('FYROM', 'Former Yugoslav Republic of Macedonia'))
# ace_countries.append(('MK', 'Republic of Macedonia'))

ace_countries.append(("MK", "Republic of North Macedonia"))

ace_countries.append(
    ("XK", "Kosovo under UN Security Council Resolution 1244/99"))
ace_countries_dict = dict(ace_countries)

ace_countries_vocabulary = generic_vocabulary(ace_countries)
alsoProvides(ace_countries_vocabulary, IVocabularyFactory)


eu_countries_selection = [
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IS",
    "IE",
    "IT",
    "LV",
    "LI",
    "LT",
    "LU",
    "MT",
    "NL",
    "NO",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
    "CH",
    "TR",
    "GB",
]

# Used for dropdowns
ace_countries_selection = [
    (x.alpha_2, x.name)
    for x in pycountry.countries
    if x.alpha_2 in eu_countries_selection
]
ace_countries_selection = [x for x in ace_countries_selection if x[0] != "CZ"]
ace_countries_selection.append(("CZ", "Czechia"))
ace_countries_selection = sorted(ace_countries_selection, key=lambda x: x[0])

# Used for faceted search in /data-and-downloads
faceted_countries = [
    "AL",
    "AT",
    "BE",
    "BG",
    "BA",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IS",
    "IE",
    "IT",
    "LV",
    "LI",
    "LT",
    "LU",
    "MT",
    "ME",
    "NL",
    "NO",
    "PL",
    "PT",
    "RO",
    "RS",
    "SK",
    "SI",
    "ES",
    "SE",
    "CH",
    "TR",
    "GB",
]
faceted_countries = [
    (x.alpha_2, x.name) for x in pycountry.countries if x.alpha_2 in faceted_countries
]
faceted_countries.append(("MK", "Republic of North Macedonia"))
faceted_countries.append(
    ("XK", "Kosovo under UN Security Council Resolution 1244/99"))

faceted_countries_dict = dict(faceted_countries)

faceted_countries_vocabulary = generic_vocabulary(faceted_countries)
alsoProvides(faceted_countries_vocabulary, IVocabularyFactory)

_measure_types = (("A", "Case study"), ("M", "Adaptation option"))
acemeasure_types = generic_vocabulary(_measure_types)
alsoProvides(acemeasure_types, IVocabularyFactory)

_origin_website = (
    ("AdapteCCA", "AdapteCCA"),
    # ("Climate-ADAPT", "Climate-ADAPT"),
    ("EEA", "EEA"),
    ("EEA-archived", "EEA-archived"),
    ("DRMKC", "DRMKC"),
    ("C3S", "C3S"),
    ("Lancet Countdown", "Lancet Countdown"),
)
origin_website = generic_vocabulary(_origin_website)
alsoProvides(origin_website, IVocabularyFactory)

_health_impacts = (
    ("Heat", _("Heat")),
    ("Droughts and floods", _("Droughts and floods")),
    ("Climate-sensitive diseases", _("Climate-sensitive diseases")),
    ("Air pollution and aero-allergens", _("Air pollution and aero-allergens")),
    ("Wildfires", _("Wildfires")),
    ("-NONSPECIFIC-", _("-NONSPECIFIC-")),
)

health_impacts = generic_vocabulary(_health_impacts, False)
alsoProvides(health_impacts, IVocabularyFactory)

_key_community_systems = (
    ("Critical Infrastructure", _("Critical Infrastructure")),
    ("Health and Wellbeing", _("Health and Wellbeing")),
    ("Land-use and Food Systems", _("Land-use and Food Systems")),
    ("Water Management", _("Water Management")),
    (
        "Ecosystems and Nature Based Solutions",
        _("Ecosystems and Nature Based Solutions"),
    ),
    ("Local Economic Systems", _("Local Economic Systems")),
)

key_community_systems = generic_vocabulary(_key_community_systems, False)
alsoProvides(key_community_systems, IVocabularyFactory)

_climate_threats = (
    ("Mean air temperature", _("Mean air temperature")),
    ("Extreme heat", _("Extreme heat")),
    ("Cold spells and frost", _("Cold spells and frost")),
    ("Mean precipitation", _("Mean precipitation")),
    ("Extreme Precipitation", _("Extreme Precipitation")),
    ("River flooding", _("River flooding")),
    ("Aridity", _("Aridity")),
    ("Wildfire", _("Wildfire")),
    ("Snow and ice", _("Snow and ice")),
    ("Relative sea level", _("Relative sea level")),
    ("Coastal flooding", _("Coastal flooding")),
)

climate_threats = generic_vocabulary(_climate_threats, False)
alsoProvides(climate_threats, IVocabularyFactory)

_funding_programme = (
    ("Other", "Other"),
    ("COST Action", "COST Action"),
    ("LIFE - Environment and climate action",
     "LIFE - Environment and climate action"),
    (
        "COPERNICUS - European earth observation programme",
        "COPERNICUS - European earth observation programme",
    ),
    (
        "FP5: 1998/2002 - Fifth Framework Programme",
        "FP5: 1998/2002 - Fifth Framework Programme",
    ),
    ("HORIZON 2020", "HORIZON 2020"),
    ("INTERREG", "INTERREG"),
    ("National Funding", "National Funding"),
    (
        "FP7: 2007/2013 - Seventh Framework Programme",
        "FP7: 2007/2013 - Seventh Framework Programme",
    ),
    (
        "FP6: 2002/2006 - Sixth Framework Programme",
        "FP6: 2002/2006 - Sixth Framework Programme",
    ),
    ("Horizon Europe", "Horizon Europe"),
)

funding_programme = generic_vocabulary(_funding_programme)
alsoProvides(funding_programme, IVocabularyFactory)

_cca_types = [
    ("DOCUMENT", "Publication & Report"),
    ("INFORMATIONSOURCE", "Information Portal"),
    ("GUIDANCE", "Guidance Document"),
    ("TOOL", "Tool"),
    ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
    ("INDICATOR", "Indicators"),
    ("RESEARCHPROJECT", "Research and Knowledge Projects"),
    ("MEASURE", "Adaptation Option"),
    ("ACTION", "Case Studies"),
    ("ORGANISATION", "Organisation"),
    ("NEW", "News"),
    ("EVENT", "Events"),
    # ("VIDEOS", "Videos"),
]
cca_types = generic_vocabulary(_cca_types)
alsoProvides(cca_types, IVocabularyFactory)

_a = namedtuple("_AceItemType", ["id", "label"])
aceitem_types = [_a(*x) for x in _cca_types]

SpecialTagsVocabularyFactory = KeywordsVocabulary("special_tags")
KeywordsVocabularyFactory = KeywordsVocabulary("keywords")
ObjectProvidesVocabulary = KeywordsVocabulary("object_provides")
UpdatingNotesVocabularyFactory = KeywordsVocabulary("updating_notes")

_governance = [
    ("TRANS", "Transnational region (stretching across country borders)"),
    ("NAT", "National"),
    ("SNA", "Sub National Regions"),
    ("LC", "Local (e.g. city or municipal level)"),
]
governance_level = generic_vocabulary(_governance)
alsoProvides(governance_level, IVocabularyFactory)

_language = [
    ("English", "English"),
    ("German", "German"),
    ("French", "French"),
    ("Spanish", "Spanish"),
    ("Italian", "Italian"),
    ("Polish", "Polish"),
    ("Bulgarian", "Bulgarian"),
    ("Dutch", "Dutch"),
    ("Romanian", "Romanian"),
    ("Slovak", "Slovak"),
    ("Slovenian", "Slovenian"),
]
language = generic_vocabulary(_language)
alsoProvides(language, IVocabularyFactory)


_category = [
    (
        "Grey",
        "Grey: technological and engineering solutions aiming mainly at the protection of infrastructures or people.",
    ),
    (
        "Green",
        "Green: ecosystem-based approaches that use the multiple services of nature aiming at raising the resilience of ecosystems and their services.",
    ),
    (
        "Soft",
        "Soft: managerial, legal and policy approaches that alter human behavior and styles of governance (e.g. spatial planning and policies), including financial/fiscal instruments, such as insurance",
    ),
]
category = generic_vocabulary(_category)
alsoProvides(category, IVocabularyFactory)

_key_type_measures = [
    ("A1", _("A1: Governance and Institutional: Policy Instruments")),
    ("A2", _("A2: Governance and Institutional: Management and planning")),
    (
        "A3",
        _("A3: Governance and Institutional: Coordination cooperation and networks"),
    ),
    ("B1", _("B1: Economic and Finance: Financing incentive instruments")),
    ("B2", _("B2: Economic and Finance: Insurance and risk sharing instruments")),
    ("C1", _("C1: Physical and technological: Grey options")),
    ("C2", _("C2: Physical and technological: Technological options")),
    (
        "D1",
        _("D1: Nature based Solutions and Ecosystem based approaches: Green options"),
    ),
    (
        "D2",
        _("D2: Nature based Solutions and Ecosystem based approaches: Blue options"),
    ),
    (
        "E1",
        _("E1: Knowledge and behavioural change: Information and awareness raising"),
    ),
    (
        "E2",
        _(
            "E2: Knowledge and behavioural change: Capacity building empowering and lifestyle practices"
        ),
    ),
]
key_type_measures = generic_vocabulary(_key_type_measures)
alsoProvides(key_type_measures, IVocabularyFactory)

_key_type_measures_short = [
    ("A1", _("A1: Policy Instruments")),
    ("A2", _("A2: Management and planning")),
    ("A3", _("A3: Coordination cooperation and networks")),
    ("B1", _("B1: Financing incentive instruments")),
    ("B2", _("B2: Insurance and risk sharing instruments")),
    ("C1", _("C1: Grey options")),
    ("C2", _("C2: Technological options")),
    ("D1", _("D1: Green options")),
    ("D2", _("D2: Blue options")),
    ("E1", _("E1: Information and awareness raising")),
    ("E2", _("E2: Capacity building empowering and lifestyle practices")),
]
key_type_measures_short = generic_vocabulary(_key_type_measures_short)
alsoProvides(key_type_measures_short, IVocabularyFactory)

_ipcc_category = [
    (
        "STRUCT_ENG",
        _("Structural and physical: Engineering and built environment options"),
    ),
    ("STRUCT_TECH", _("Structural and physical: Technological options")),
    ("STRUCT_ECO", _("Structural and physical: Ecosystem-based adaptation options")),
    ("STRUCT_SER", _("Structural and physical: Service options")),
    ("SOC_EDU", _("Social: Educational options")),
    ("SOC_INF", _("Social: Informational")),
    ("SOC_BEH", _("Social: Behavioural")),
    ("INS_ECO", _("Institutional: Economic options")),
    ("INS_LAW", _("Institutional: Law and regulations")),
    ("INS_GOV", _("Institutional: Government policies and programmes")),
]
ipcc_category = generic_vocabulary(_ipcc_category)
alsoProvides(ipcc_category, IVocabularyFactory)


_header_level = (
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
    ("h4", "Header 4"),
    ("h5", "Header 5"),
)
rich_header_level = generic_vocabulary(_header_level)
alsoProvides(rich_header_level, IVocabularyFactory)

labels = """
acesearch-geochars-lbl-GLOBAL=Global
acesearch-geochars-lbl-EUROPE=Europe
acesearch-geochars-lbl-MACRO_TRANSNATIONAL_REGION=Macro-Transnational Regions
acesearch-geochars-lbl-BIOGRAPHICAL_REGION=Biogeographical Regions
acesearch-geochars-lbl-COUNTRIES=Countries
acesearch-geochars-lbl-SUBNATIONAL=Subnational Regions
acesearch-geochars-lbl-CITY=Municipality Name
acesearch-geochars-lbl-TRANS_MACRO_NORTHPERI=Northern Periphery and Arctic
acesearch-geochars-lbl-TRANS_MACRO_BACLITC=Baltic Sea
acesearch-geochars-lbl-TRANS_MACRO_NW_EUROPE=North West Europe
acesearch-geochars-lbl-TRANS_MACRO_N_SEA=North Sea
acesearch-geochars-lbl-TRANS_MACRO_ATL_AREA=Atlantic Area
acesearch-geochars-lbl-TRANS_MACRO_ALP_SPACE=Alpine Space
acesearch-geochars-lbl-TRANS_MACRO_CEN_EUR=Central Europe
acesearch-geochars-lbl-TRANS_MACRO_SW_EUR=South West Europe
acesearch-geochars-lbl-TRANS_MACRO_MED=Mediterranean (Euro-Med)
acesearch-geochars-lbl-TRANS_MACRO_DANUBE=Danube Area
acesearch-geochars-lbl-TRANS_MACRO_ADR_IONIAN=Adriatic-Ionian
acesearch-geochars-lbl-TRANS_MACRO_MED_BASIN=Mediterranean Sea Basin (NEXT)
acesearch-geochars-lbl-TRANS_MACRO_BLACKSEA_BASIN=Black Sea Basin (NEXT)
acesearch-geochars-lbl-TRANS_MACRO_OUTERMOST=Outermost Regions
acesearch-geochars-lbl-TRANS_BIO_ALPINE=Alpine
acesearch-geochars-lbl-TRANS_BIO_ANATOLIAN=Anatolian
acesearch-geochars-lbl-TRANS_BIO_ARCTIC=Arctic
acesearch-geochars-lbl-TRANS_BIO_ATLANTIC=Atlantic
acesearch-geochars-lbl-TRANS_BIO_BLACKSEA=Black Sea
acesearch-geochars-lbl-TRANS_BIO_BOREAL=Boreal
acesearch-geochars-lbl-TRANS_BIO_CONTINENTAL=Continental
acesearch-geochars-lbl-TRANS_BIO_MACARO=Macaronesia
acesearch-geochars-lbl-TRANS_BIO_MEDIT=Mediterranean
acesearch-geochars-lbl-TRANS_BIO_PANNONIAN=Pannonian
acesearch-geochars-lbl-TRANS_BIO_STEPPIC=Steppic
"""

# (u'TRANS_MACRO_ADR_IONIAN',
#  u'TRANS_MACRO_ALP_SPACE',
#  u'TRANS_MACRO_ATL_AREA',
#  u'TRANS_MACRO_BACLITC',
#  u'TRANS_MACRO_BALKAN_MED',
#  u'TRANS_MACRO_BLACKSEA_BASIN',
#  u'TRANS_MACRO_CEN_EUR',
#  u'TRANS_MACRO_DANUBE',
#  u'TRANS_MACRO_MED',
#  u'TRANS_MACRO_MED_BASIN',
#  u'TRANS_MACRO_MID_ATLANTIC',
#  u'TRANS_MACRO_NORTHPERI',
#  u'TRANS_MACRO_NW_EUROPE',
#  u'TRANS_MACRO_N_SEA',
#  u'TRANS_MACRO_OUTERMOST',
#  u'TRANS_MACRO_SW_EUR')

BIOREGIONS = {}

for line in [_f for _f in labels.split("\n") if _f]:
    first, label = line.split("=")
    name = first.split("-lbl-")[1]
    BIOREGIONS[name] = label

REMAPED_BIOREGIONS = {
    # 'TRANS_MACRO_MED_BASIN': 'Mediterranean',
    "TRANS_MACRO_BLACKSEA_BASIN": "Black Sea Basin",
    "TRANS_MACRO_DANUBE": "Danube",
    "TRANS_MACRO_MED": "Mediterranean",
    "TRANS_MACRO_MED_BASIN": "Mediterranean Sea Basin",
    "TRANS_MACRO_NORTHPERI": "Northern Periphery",
}


SUBNATIONAL_REGIONS = {
    "SUBN_Région_de_Bruxelles_Capit": "Région de Bruxelles-Capitale/Brussels Hoofdstedelijk Gewest (BE)",
    "SUBN_Prov__Antwerpen__BE_": "Prov. Antwerpen (BE)",
    "SUBN_Prov__Limburg__BE___BE_": "Prov. Limburg (BE) (BE)",
    "SUBN_Prov__Oost_Vlaanderen__BE": "Prov. Oost-Vlaanderen (BE)",
    "SUBN_Prov__Vlaams_Brabant__BE_": "Prov. Vlaams-Brabant (BE)",
    "SUBN_Prov__West_Vlaanderen__BE": "Prov. West-Vlaanderen (BE)",
    "SUBN_Prov__Brabant_Wallon__BE_": "Prov. Brabant Wallon (BE)",
    "SUBN_Prov__Hainaut__BE_": "Prov. Hainaut (BE)",
    "SUBN_Prov__Liège__BE_": "Prov. Liège (BE)",
    "SUBN_Prov__Luxembourg__BE___BE": "Prov. Luxembourg (BE) (BE)",
    "SUBN_Prov__Namur__BE_": "Prov. Namur (BE)",
    "SUBN_Extra_Regio_NUTS_2__BE_": "Extra-Regio NUTS 2 (BE)",
    "SUBN_Северозападен__Severozapa": "Северозападен (Severozapaden) (BG)",
    "SUBN_Северен_централен__Severe": "Северен централен (Severen tsentralen) (BG)",
    "SUBN_Североизточен__Severoizto": "Североизточен (Severoiztochen) (BG)",
    "SUBN_Югоизточен__Yugoiztochen_": "Югоизточен (Yugoiztochen) (BG)",
    "SUBN_Югозападен__Yugozapaden__": "Югозападен (Yugozapaden) (BG)",
    "SUBN_Южен_централен__Yuzhen_ts": "Южен централен (Yuzhen tsentralen) (BG)",
    "SUBN_Extra_Regio_NUTS_2__BG_": "Extra-Regio NUTS 2 (BG)",
    "SUBN_Région_lémanique_CH_": "Région lémanique (CH)",
    "SUBN_Espace_Mittelland_CH_": "Espace Mittelland (CH)",
    "SUBN_Nordwestschweiz_CH_": "Nordwestschweiz (CH)",
    "SUBN_Zürich_CH_": "Zürich (CH)",
    "SUBN_Ostschweiz_CH_": "Ostschweiz (CH)",
    "SUBN_Zentralschweiz_CH_": "Zentralschweiz (CH)",
    "SUBN_Ticino_CH_": "Ticino (CH)",
    "SUBN_Praha__CZ_": "Praha (CZ)",
    "SUBN_Střední_Čechy__CZ_": "Střední Čechy (CZ)",
    "SUBN_Jihozápad__CZ_": "Jihozápad (CZ)",
    "SUBN_Severozápad__CZ_": "Severozápad (CZ)",
    "SUBN_Severovýchod__CZ_": "Severovýchod (CZ)",
    "SUBN_Jihovýchod__CZ_": "Jihovýchod (CZ)",
    "SUBN_Střední_Morava__CZ_": "Střední Morava (CZ)",
    "SUBN_Moravskoslezsko__CZ_": "Moravskoslezsko (CZ)",
    "SUBN_Extra_Regio_NUTS_2__CZ_": "Extra-Regio NUTS 2 (CZ)",
    "SUBN_Hovedstaden__DK_": "Hovedstaden (DK)",
    "SUBN_Sjælland__DK_": "Sjælland (DK)",
    "SUBN_Syddanmark__DK_": "Syddanmark (DK)",
    "SUBN_Midtjylland__DK_": "Midtjylland (DK)",
    "SUBN_Nordjylland__DK_": "Nordjylland (DK)",
    "SUBN_Extra_Regio_NUTS_2__DK_": "Extra-Regio NUTS 2 (DK)",
    "SUBN_Stuttgart__DE_": "Stuttgart (DE)",
    "SUBN_Karlsruhe__DE_": "Karlsruhe (DE)",
    "SUBN_Freiburg__DE_": "Freiburg (DE)",
    "SUBN_Tübingen__DE_": "Tübingen (DE)",
    "SUBN_Oberbayern__DE_": "Oberbayern (DE)",
    "SUBN_Niederbayern__DE_": "Niederbayern (DE)",
    "SUBN_Oberpfalz__DE_": "Oberpfalz (DE)",
    "SUBN_Oberfranken__DE_": "Oberfranken (DE)",
    "SUBN_Mittelfranken__DE_": "Mittelfranken (DE)",
    "SUBN_Unterfranken__DE_": "Unterfranken (DE)",
    "SUBN_Schwaben__DE_": "Schwaben (DE)",
    "SUBN_Berlin__DE_": "Berlin (DE)",
    "SUBN_Brandenburg__DE_": "Brandenburg (DE)",
    "SUBN_Bremen__DE_": "Bremen (DE)",
    "SUBN_Hamburg__DE_": "Hamburg (DE)",
    "SUBN_Darmstadt__DE_": "Darmstadt (DE)",
    "SUBN_Gießen__DE_": "Gießen (DE)",
    "SUBN_Kassel__DE_": "Kassel (DE)",
    "SUBN_Mecklenburg_Vorpommern__D": "Mecklenburg-Vorpommern (DE)",
    "SUBN_Braunschweig__DE_": "Braunschweig (DE)",
    "SUBN_Hannover__DE_": "Hannover (DE)",
    "SUBN_Lüneburg__DE_": "Lüneburg (DE)",
    "SUBN_Weser_Ems__DE_": "Weser-Ems (DE)",
    "SUBN_Düsseldorf__DE_": "Düsseldorf (DE)",
    "SUBN_Köln__DE_": "Köln (DE)",
    "SUBN_Münster__DE_": "Münster (DE)",
    "SUBN_Detmold__DE_": "Detmold (DE)",
    "SUBN_Arnsberg__DE_": "Arnsberg (DE)",
    "SUBN_Koblenz__DE_": "Koblenz (DE)",
    "SUBN_Trier__DE_": "Trier (DE)",
    "SUBN_Rheinhessen_Pfalz__DE_": "Rheinhessen-Pfalz (DE)",
    "SUBN_Saarland__DE_": "Saarland (DE)",
    "SUBN_Dresden__DE_": "Dresden (DE)",
    "SUBN_Chemnitz__DE_": "Chemnitz (DE)",
    "SUBN_Leipzig__DE_": "Leipzig (DE)",
    "SUBN_Sachsen_Anhalt__DE_": "Sachsen-Anhalt (DE)",
    "SUBN_Schleswig_Holstein__DE_": "Schleswig-Holstein (DE)",
    "SUBN_Thüringen__DE_": "Thüringen (DE)",
    "SUBN_Extra_Regio_NUTS_2__DE_": "Extra-Regio NUTS 2 (DE)",
    "SUBN_Eesti__EE_": "Eesti (EE)",
    "SUBN_Extra_Regio_NUTS_2__EE_": "Extra-Regio NUTS 2 (EE)",
    "SUBN_Border__Midland_and_Weste": "Border, Midland and Western (IE)",
    "SUBN_Southern_and_Eastern__IE_": "Southern and Eastern (IE)",
    "SUBN_Extra_Regio_NUTS_2__IE_": "Extra-Regio NUTS 2 (IE)",
    "SUBN_Aττική__Attiki__GR_": "Aττική (Attiki) (GR)",
    "SUBN_Βόρειο_Αιγαίο__Voreio_Aig__GR_": "Βόρειο Αιγαίο (Voreio Aigaio) (GR)",
    "SUBN_Νότιο_Αιγαίο__Notio_Aigai__GR_": "Νότιο Αιγαίο (Notio Aigaio) (GR)",
    "SUBN_Κρήτη__Kriti__GR_": "Κρήτη (Kriti) (GR)",
    "SUBN_Aνατολική_Μακεδονία__Θράκ__GR_": "Aνατολική Μακεδονία, Θράκη (Anatoliki Makedonia, Thraki) (GR)",
    "SUBN_Κεντρική_Μακεδονία__Kentr__GR_": "Κεντρική Μακεδονία (Kentriki Makedonia) (GR)",
    "SUBN_Δυτική_Μακεδονία__Dytiki__GR_": "Δυτική Μακεδονία (Dytiki Makedonia) (GR)",
    "SUBN_Θεσσαλία__Thessalia__GR_": "Θεσσαλία (Thessalia) (GR)",
    "SUBN_Ιόνια_Νησιά__Ionia_Nisia__GR_": "Ιόνια Νησιά (Ionia Nisia) (GR)",
    "SUBN_Δυτική_Ελλάδα__Dytiki_Ell__GR_": "Δυτική Ελλάδα (Dytiki Ellada) (GR)",
    "SUBN_Στερεά_Ελλάδα__Sterea_Ell__GR_": "Στερεά Ελλάδα (Sterea Ellada) (GR)",
    "SUBN_Πελοπόννησος__Peloponniso__GR_": "Πελοπόννησος (Peloponnisos) (GR)",
    "SUBN_Extra_Regio_NUTS_2__GR_": "Extra-Regio NUTS 2 (GR)",
    "SUBN_Galicia__ES_": "Galicia (ES)",
    "SUBN_Principado_de_Asturias__E": "Principado de Asturias (ES)",
    "SUBN_Cantabria__ES_": "Cantabria (ES)",
    "SUBN_País_Vasco__ES_": "País Vasco (ES)",
    "SUBN_Comunidad_Foral_de_Navarr": "Comunidad Foral de Navarra (ES)",
    "SUBN_La_Rioja__ES_": "La Rioja (ES)",
    "SUBN_Aragón__ES_": "Aragón (ES)",
    "SUBN_Comunidad_de_Madrid__ES_": "Comunidad de Madrid (ES)",
    "SUBN_Castilla_y_León__ES_": "Castilla y León (ES)",
    "SUBN_Castilla_La_Mancha__ES_": "Castilla-La Mancha (ES)",
    "SUBN_Extremadura__ES_": "Extremadura (ES)",
    "SUBN_Cataluña__ES_": "Cataluña (ES)",
    "SUBN_Comunidad_Valenciana__ES_": "Comunidad Valenciana (ES)",
    "SUBN_Illes_Balears__ES_": "Illes Balears (ES)",
    "SUBN_Andalucía__ES_": "Andalucía (ES)",
    "SUBN_Región_de_Murcia__ES_": "Región de Murcia (ES)",
    "SUBN_Ciudad_Autónoma_de_Ceuta_": "Ciudad Autónoma de Ceuta (ES)",
    "SUBN_Ciudad_Autónoma_de_Melill": "Ciudad Autónoma de Melilla (ES)",
    "SUBN_Canarias__ES_": "Canarias (ES)",
    "SUBN_Extra_Regio_NUTS_2__ES_": "Extra-Regio NUTS 2 (ES)",
    "SUBN_Île_de_France__FR_": "Île de France (FR)",
    "SUBN_Champagne_Ardenne__FR_": "Champagne-Ardenne (FR)",
    "SUBN_Picardie__FR_": "Picardie (FR)",
    "SUBN_Haute_Normandie__FR_": "Haute-Normandie (FR)",
    "SUBN_Centre__FR_": "Centre (FR)",
    "SUBN_Basse_Normandie__FR_": "Basse-Normandie (FR)",
    "SUBN_Bourgogne__FR_": "Bourgogne (FR)",
    "SUBN_Nord___Pas_de_Calais__FR_": "Nord - Pas-de-Calais (FR)",
    "SUBN_Lorraine__FR_": "Lorraine (FR)",
    "SUBN_Alsace__FR_": "Alsace (FR)",
    "SUBN_Franche_Comté__FR_": "Franche-Comté (FR)",
    "SUBN_Pays_de_la_Loire__FR_": "Pays de la Loire (FR)",
    "SUBN_Bretagne__FR_": "Bretagne (FR)",
    "SUBN_Poitou_Charentes__FR_": "Poitou-Charentes (FR)",
    "SUBN_Aquitaine__FR_": "Aquitaine (FR)",
    "SUBN_Midi_Pyrénées__FR_": "Midi-Pyrénées (FR)",
    "SUBN_Limousin__FR_": "Limousin (FR)",
    "SUBN_Rhône_Alpes__FR_": "Rhône-Alpes (FR)",
    "SUBN_Auvergne__FR_": "Auvergne (FR)",
    "SUBN_Languedoc_Roussillon__FR_": "Languedoc-Roussillon (FR)",
    "SUBN_Provence_Alpes_Côte_d_Azu": "Provence-Alpes-Côte d'Azur (FR)",
    "SUBN_Corse__FR_": "Corse (FR)",
    "SUBN_Guadeloupe__FR_": "Guadeloupe (FR)",
    "SUBN_Martinique__FR_": "Martinique (FR)",
    "SUBN_Guyane__FR_": "Guyane (FR)",
    "SUBN_Réunion__FR_": "Réunion (FR)",
    "SUBN_Extra_Regio_NUTS_2__FR_": "Extra-Regio NUTS 2 (FR)",
    "SUBN_Extra_Regio_NUTS_2__HR_": "Extra-Regio NUTS 2 (HR)",
    "SUBN_Piemonte__IT_": "Piemonte (IT)",
    "SUBN_Valle_d_Aosta_Vallée_d_Ao": "Valle d'Aosta/Vallée d'Aoste (IT)",
    "SUBN_Liguria__IT_": "Liguria (IT)",
    "SUBN_Lombardia__IT_": "Lombardia (IT)",
    "SUBN_Abruzzo__IT_": "Abruzzo (IT)",
    "SUBN_Molise__IT_": "Molise (IT)",
    "SUBN_Campania__IT_": "Campania (IT)",
    "SUBN_Puglia__IT_": "Puglia (IT)",
    "SUBN_Basilicata__IT_": "Basilicata (IT)",
    "SUBN_Calabria__IT_": "Calabria (IT)",
    "SUBN_Sicilia__IT_": "Sicilia (IT)",
    "SUBN_Sardegna__IT_": "Sardegna (IT)",
    "SUBN_Provincia_Autonoma_di_Bol": "Provincia Autonoma di Bolzano/Bozen (IT)",
    "SUBN_Provincia_Autonoma_di_Tre": "Provincia Autonoma di Trento (IT)",
    "SUBN_Veneto__IT_": "Veneto (IT)",
    "SUBN_Friuli_Venezia_Giulia__IT": "Friuli-Venezia Giulia (IT)",
    "SUBN_Emilia_Romagna__IT_": "Emilia-Romagna (IT)",
    "SUBN_Toscana__IT_": "Toscana (IT)",
    "SUBN_Umbria__IT_": "Umbria (IT)",
    "SUBN_Marche__IT_": "Marche (IT)",
    "SUBN_Lazio__IT_": "Lazio (IT)",
    "SUBN_Pisa__IT_": "Pisa (IT)",
    "SUBN_Extra_Regio_NUTS_2__IT_": "Extra-Regio NUTS 2 (IT)",
    "SUBN_Ísland_IS_": "Ísland (IS)",
    "SUBN_Liechtenstein_LI_": "Liechtenstein (LI)",
    "SUBN_Κύπρος__Kýpros___CY_": "Κύπρος (Kýpros) (CY)",
    "SUBN_Extra_Regio_NUTS_2__CY_": "Extra-Regio NUTS 2 (CY)",
    "SUBN_Latvija__LV_": "Latvija (LV)",
    "SUBN_Extra_Regio_NUTS_2__LV_": "Extra-Regio NUTS 2 (LV)",
    "SUBN_Lietuva__LT_": "Lietuva (LT)",
    "SUBN_Extra_Regio_NUTS_2__LT_": "Extra-Regio NUTS 2 (LT)",
    "SUBN_Luxembourg__LU_": "Luxembourg (LU)",
    "SUBN_Extra_Regio_NUTS_2__LU_": "Extra-Regio NUTS 2 (LU)",
    "SUBN_Közép_Magyarország__HU_": "Közép-Magyarország (HU)",
    "SUBN_Közép_Dunántúl__HU_": "Közép-Dunántúl (HU)",
    "SUBN_Nyugat_Dunántúl__HU_": "Nyugat-Dunántúl (HU)",
    "SUBN_Dél_Dunántúl__HU_": "Dél-Dunántúl (HU)",
    "SUBN_Észak_Magyarország__HU_": "Észak-Magyarország (HU)",
    "SUBN_Észak_Alföld__HU_": "Észak-Alföld (HU)",
    "SUBN_Dél_Alföld__HU_": "Dél-Alföld (HU)",
    "SUBN_Extra_Regio_NUTS_2__HU_": "Extra-Regio NUTS 2 (HU)",
    "SUBN_Malta__MT_": "Malta (MT)",
    "SUBN_Extra_Regio_NUTS_2__MT_": "Extra-Regio NUTS 2 (MT)",
    "SUBN_Црна_Гора_Crna_Gora_ME_": "Црна Гора (Crna Gora) (ME)",
    "SUBN_Поранешна_југословенска_Република_Македонија_Poranešna_jugoslovenska_Republika_Makedonija_MK_": "Поранешна југословенска Република Македонија (Poranešna jugoslovenska Republika Makedonija) (MK)",
    "SUBN_Friesland__NL___NL_": "Friesland (NL) (NL)",
    "SUBN_Groningen__NL_": "Groningen (NL)",
    "SUBN_Drenthe__NL_": "Drenthe (NL)",
    "SUBN_Overijssel__NL_": "Overijssel (NL)",
    "SUBN_Gelderland__NL_": "Gelderland (NL)",
    "SUBN_Flevoland__NL_": "Flevoland (NL)",
    "SUBN_Utrecht__NL_": "Utrecht (NL)",
    "SUBN_Noord_Holland__NL_": "Noord-Holland (NL)",
    "SUBN_Zuid_Holland__NL_": "Zuid-Holland (NL)",
    "SUBN_Zeeland__NL_": "Zeeland (NL)",
    "SUBN_Noord_Brabant__NL_": "Noord-Brabant (NL)",
    "SUBN_Limburg__NL___NL_": "Limburg (NL) (NL)",
    "SUBN_Extra_Regio_NUTS_2__NL_": "Extra-Regio NUTS 2 (NL)",
    "SUBN_Oslo_og_Akershus_NO_": "Oslo og Akershus (NO)",
    "SUBN_Hedmark_og_Oppland_NO_": "Hedmark og Oppland (NO)",
    "SUBN_Sør_Østlandet_NO_": "Sør-Østlandet (NO)",
    "SUBN_Agder_og_Rogaland_NO_": "Agder og Rogaland (NO)",
    "SUBN_Vestlandet_NO_": "Vestlandet (NO)",
    "SUBN_Trøndelag_NO_": "Trøndelag (NO)",
    "SUBN_Nord_Norge_NO_": "Nord-Norge (NO)",
    "SUBN_Burgenland__AT___AT_": "Burgenland (AT) (AT)",
    "SUBN_Niederösterreich__AT_": "Niederösterreich (AT)",
    "SUBN_Wien__AT_": "Wien (AT)",
    "SUBN_Kärnten__AT_": "Kärnten (AT)",
    "SUBN_Steiermark__AT_": "Steiermark (AT)",
    "SUBN_Oberösterreich__AT_": "Oberösterreich (AT)",
    "SUBN_Salzburg__AT_": "Salzburg (AT)",
    "SUBN_Tirol__AT_": "Tirol (AT)",
    "SUBN_Vorarlberg__AT_": "Vorarlberg (AT)",
    "SUBN_Extra_Regio_NUTS_2__AT_": "Extra-Regio NUTS 2 (AT)",
    "SUBN_Veri_AL_": "Veri (AL)",
    "SUBN_Qender_AL_": "Qender (AL)",
    "SUBN_Jug_AL_": "Jug (AL)",
    "SUBN_Łódzkie__PL_": "Łódzkie (PL)",
    "SUBN_Mazowieckie__PL_": "Mazowieckie (PL)",
    "SUBN_Małopolskie__PL_": "Małopolskie (PL)",
    "SUBN_Śląskie__PL_": "Śląskie (PL)",
    "SUBN_Lubelskie__PL_": "Lubelskie (PL)",
    "SUBN_Podkarpackie__PL_": "Podkarpackie (PL)",
    "SUBN_Świętokrzyskie__PL_": "Świętokrzyskie (PL)",
    "SUBN_Podlaskie__PL_": "Podlaskie (PL)",
    "SUBN_Wielkopolskie__PL_": "Wielkopolskie (PL)",
    "SUBN_Zachodniopomorskie__PL_": "Zachodniopomorskie (PL)",
    "SUBN_Lubuskie__PL_": "Lubuskie (PL)",
    "SUBN_Dolnośląskie__PL_": "Dolnośląskie (PL)",
    "SUBN_Opolskie__PL_": "Opolskie (PL)",
    "SUBN_Kujawsko_Pomorskie__PL_": "Kujawsko-Pomorskie (PL)",
    "SUBN_Warmińsko_Mazurskie__PL_": "Warmińsko-Mazurskie (PL)",
    "SUBN_Pomorskie__PL_": "Pomorskie (PL)",
    "SUBN_Extra_Regio_NUTS_2__PL_": "Extra-Regio NUTS 2 (PL)",
    "SUBN_Norte__PT_": "Norte (PT)",
    "SUBN_Algarve__PT_": "Algarve (PT)",
    "SUBN_Centro__PT___PT_": "Centro (PT) (PT)",
    "SUBN_Lisboa__PT_": "Lisboa (PT)",
    "SUBN_Alentejo__PT_": "Alentejo (PT)",
    "SUBN_Região_Autónoma_dos_Açore": "Região Autónoma dos Açores (PT)",
    "SUBN_Região_Autónoma_da_Madeir": "Região Autónoma da Madeira (PT)",
    "SUBN_Extra_Regio_NUTS_2__PT_": "Extra-Regio NUTS 2 (PT)",
    "SUBN_Nord_Vest__RO_": "Nord-Vest (RO)",
    "SUBN_Centru__RO_": "Centru (RO)",
    "SUBN_Nord_Est__RO_": "Nord-Est (RO)",
    "SUBN_Sud_Est__RO_": "Sud-Est (RO)",
    "SUBN_Sud___Muntenia__RO_": "Sud - Muntenia (RO)",
    "SUBN_Bucureşti___Ilfov__RO_": "Bucureşti - Ilfov (RO)",
    "SUBN_Sud_Vest_Oltenia__RO_": "Sud-Vest Oltenia (RO)",
    "SUBN_Vest__RO_": "Vest (RO)",
    "SUBN_Extra_Regio_NUTS_2__RO_": "Extra-Regio NUTS 2 (RO)",
    "SUBN_Beogradski_region_RS_": "Beogradski region (RS)",
    "SUBN_Region_Vojvodine_RS_": "Region Vojvodine (RS)",
    "SUBN_Region_Šumadije_iZapadne_Srbije_RS_": "Region Šumadije iZapadne Srbije (RS)",
    "SUBN_Region_Južne_i_Istočne_Srbije_RS_": "Region Južne i Istočne Srbije (RS)",
    "SUBN_Vzhodna_Slovenija__SI_": "Vzhodna Slovenija (SI)",
    "SUBN_Zahodna_Slovenija__SI_": "Zahodna Slovenija (SI)",
    "SUBN_Extra_Regio_NUTS_2__SI_": "Extra-Regio NUTS 2 (SI)",
    "SUBN_Bratislavský_kraj__SK_": "Bratislavský kraj (SK)",
    "SUBN_Západné_Slovensko__SK_": "Západné Slovensko (SK)",
    "SUBN_Stredné_Slovensko__SK_": "Stredné Slovensko (SK)",
    "SUBN_Východné_Slovensko__SK_": "Východné Slovensko (SK)",
    "SUBN_Extra_Regio_NUTS_2__SK_": "Extra-Regio NUTS 2 (SK)",
    "SUBN_Länsi_Suomi__FI_": "Länsi-Suomi (FI)",
    "SUBN_Helsinki_Uusimaa__FI_": "Helsinki-Uusimaa (FI)",
    "SUBN_Etelä_Suomi__FI_": "Etelä-Suomi (FI)",
    "SUBN_Pohjois__ja_Itä_Suomi__FI": "Pohjois- ja Itä-Suomi (FI)",
    "SUBN_Åland__FI_": "Åland (FI)",
    "SUBN_Extra_Regio_NUTS_2__FI_": "Extra-Regio NUTS 2 (FI)",
    "SUBN_Stockholm__SE_": "Stockholm (SE)",
    "SUBN_Östra_Mellansverige__SE_": "Östra Mellansverige (SE)",
    "SUBN_Småland_med_öarna__SE_": "Småland med öarna (SE)",
    "SUBN_Sydsverige__SE_": "Sydsverige (SE)",
    "SUBN_Västsverige__SE_": "Västsverige (SE)",
    "SUBN_Norra_Mellansverige__SE_": "Norra Mellansverige (SE)",
    "SUBN_Mellersta_Norrland__SE_": "Mellersta Norrland (SE)",
    "SUBN_Övre_Norrland__SE_": "Övre Norrland (SE)",
    "SUBN_Extra_Regio_NUTS_2__SE_": "Extra-Regio NUTS 2 (SE)",
    "SUBN_İstanbul_TR_": "İstanbul (TR)",
    "SUBN_Tekirdağ_Edirne_Kırklareli_TR_": "Tekirdağ, Edirne, Kırklareli (TR)",
    "SUBN_Balıkesir_Çanakkale_TR_": "Balıkesir, Çanakkale (TR)",
    "SUBN_İzmir_TR_": "İzmir (TR)",
    "SUBN_Aydın_Denizli_Muğla_TR_": "Aydın, Denizli, Muğla (TR)",
    "SUBN_Manisa_Afyonkarahisar_Kütahya_Uşak_TR_": "Manisa, Afyonkarahisar, Kütahya, Uşak (TR)",
    "SUBN_Bursa_Eskişehir_Bilecik_TR_": "Bursa, Eskişehir, Bilecik (TR)",
    "SUBN_Kocaeli_Sakarya_Düzce_Bolu_Yalova_TR_": "Kocaeli, Sakarya, Düzce, Bolu, Yalova (TR)",
    "SUBN_Ankara_TR_": "Ankara (TR)",
    "SUBN_Konya_Karaman_TR_": "Konya, Karaman (TR)",
    "SUBN_Antalya_Isparta_Burdur_TR_": "Antalya, Isparta, Burdur (TR)",
    "SUBN_Adana_Mersin_TR_": "Adana, Mersin (TR)",
    "SUBN_Hatay_Kahramanmaraş_Osmaniye_TR_": "Hatay, Kahramanmaraş, Osmaniye (TR)",
    "SUBN_Kırıkkale_Aksaray_Niğde_Nevşehir_Kırşehir_TR_": "Kırıkkale, Aksaray, Niğde, Nevşehir, Kırşehir (TR)",
    "SUBN_Kayseri_Sivas_Yozgat_TR_": "Kayseri, Sivas, Yozgat (TR)",
    "SUBN_Zonguldak_Karabük_Bartın_TR_": "Zonguldak, Karabük, Bartın (TR)",
    "SUBN_Kastamonu_Çankırı_Sinop_TR_": "Kastamonu, Çankırı, Sinop (TR)",
    "SUBN_Samsun_Tokat_Çorum_Amasya_TR_": "Samsun, Tokat, Çorum, Amasya (TR)",
    "SUBN_Trabzon_Ordu_Giresun_Rize_Artvin_Gümüşhane_TR_": "Trabzon, Ordu, Giresun, Rize, Artvin, Gümüşhane (TR)",
    "SUBN_Erzurum_Erzincan_Bayburt_TR_": "Erzurum, Erzincan, Bayburt (TR)",
    "SUBN_Ağrı_Kars_Iğdır_Ardahan_TR_": "Ağrı, Kars, Iğdır, Ardahan (TR)",
    "SUBN_Malatya_Elazığ_Bingöl_Tunceli_TR_": "Malatya, Elazığ, Bingöl, Tunceli (TR)",
    "SUBN_Van_Muş_Bitlis_Hakkari_TR_": "Van, Muş, Bitlis, Hakkari (TR)",
    "SUBN_Gaziantep_Adıyaman_Kilis_TR_": "Gaziantep, Adıyaman, Kilis (TR)",
    "SUBN_Şanlıurfa_Diyarbakır_TR_": "Şanlıurfa, Diyarbakır (TR)",
    "SUBN_Mardin_Batman_Şırnak_Siirt_TR_": "Mardin, Batman, Şırnak, Siirt (TR)",
    "SUBN_Tees_Valley_and_Durham__U__GB_": "Tees Valley and Durham (UK)",
    "SUBN_Northumberland_and_Tyne_a__GB_": "Northumberland and Tyne and Wear (UK)",
    "SUBN_Cumbria__GB_": "Cumbria (UK)",
    "SUBN_Greater_Manchester__GB_": "Greater Manchester (UK)",
    "SUBN_Lancashire__GB_": "Lancashire (UK)",
    "SUBN_Cheshire__GB_": "Cheshire (UK)",
    "SUBN_Merseyside__GB_": "Merseyside (UK)",
    "SUBN_East_Yorkshire_and_Northe__GB_": "East Yorkshire and Northern Lincolnshire (UK)",
    "SUBN_North_Yorkshire__GB_": "Yorkshire (UK)",
    "SUBN_West_Yorkshire__GB_": "West Yorkshire (UK)",
    "SUBN_Derbyshire_and_Nottingham__GB_": "Derbyshire and Nottinghamshire (UK)",
    "SUBN_Leicestershire__Rutland_a__GB_": "Leicestershire, Rutland and Northamptonshire (UK)",
    "SUBN_Lincolnshire__GB_": "Lincolnshire (UK)",
    "SUBN_Herefordshire__Worcesters__GB_": "Herefordshire, Worcestershire and Warwickshire (UK)",
    "SUBN_Shropshire_and_Staffordsh__GB_": "Shropshire and Staffordshire (UK)",
    "SUBN_West_Midlands__GB_": "West Midlands (UK)",
    "SUBN_East_Anglia__GB_": "East Anglia (UK)",
    "SUBN_Bedfordshire_and_Hertford__GB_": "Bedfordshire and Hertfordshire (UK)",
    "SUBN_Essex__GB_": "Essex (UK)",
    "SUBN_Inner_London_WEST__GB_": "Inner London - WEST (UK)",
    "SUBN_Inner_London_EAST__GB_": "Inner London - EAST (UK)",
    "SUBN_Outer_London_ENE__GB_": "Outer London - East and North East (UK)",
    "SUBN_Outer_London_S__GB_": "Outer - London South (UK)",
    "SUBN_Outer_London_WNW__GB_": "Outer London - West and North West (UK)",
    "SUBN_Berkshire__Buckinghamshir__GB_": "Berkshire, Buckinghamshire and Oxfordshire (UK)",
    "SUBN_Surrey__East_and_West_Sus__GB_": "Surrey, East and West Sussex (UK)",
    "SUBN_Hampshire_and_Isle_of_Wig__GB_": "Hampshire and Isle of Wight (UK)",
    "SUBN_Kent__GB_": "Kent (UK)",
    "SUBN_Gloucestershire__Wiltshir__GB_": "Gloucestershire, Wiltshire and Bristol/Bath area (UK)",
    "SUBN_Dorset_and_Somerset__GB_": "Dorset and Somerset (UK)",
    "SUBN_Cornwall_and_Isles_of_Sci__GB_": "Cornwall and Isles of Scilly (UK)",
    "SUBN_Devon__GB_": "Devon (UK)",
    "SUBN_West_Wales_and_The_Valley__GB_": "West Wales and The Valleys (UK)",
    "SUBN_East_Wales__GB_": "East Wales (UK)",
    "SUBN_Eastern_Scotland__GB_": "Eastern Scotland (UK)",
    "SUBN_South_Western_Scotland__U__GB_": "South Western Scotland (UK)",
    "SUBN_North_Eastern_Scotland__U__GB_": "North Eastern Scotland (UK)",
    "SUBN_Highlands_and_Islands__GB_": "Highlands and Islands (UK)",
    "SUBN_Northern_Ireland__GB_": "Northern Ireland (UK)",
    "SUBN_Extra_Regio_NUTS_2__GB_": "Extra-Regio NUTS 2 (UK)",
}

_rast_steps = [
    ("AST_STEP_1", _("Step 1. Preparing the ground for adaptation")),
    ("AST_STEP_2", _("Step 2. Assessing climate change risks and vulnerabilities")),
    ("AST_STEP_3", _("Step 3. Identifying adaptation options")),
    ("AST_STEP_4", _("Step 4. Assessing and selecting adaptation options")),
    ("AST_STEP_5", _("Step 5. Implementing adaptation")),
    ("AST_STEP_6", _("Step 6. Monitoring and evaluating adaptation")),
]
rast_steps_vocabulary = generic_vocabulary(_rast_steps)
alsoProvides(rast_steps_vocabulary, IVocabularyFactory)


_eligible_entities = [
    (
        "Local authorities and administrative bodies",
        _("Local authorities and administrative bodies"),
    ),
    (
        "Social, cultural and educational institutions",
        _("Social, cultural and educational institutions"),
    ),
    (
        "Companies, SMEs and private associations",
        _("Companies, SMEs and private associations"),
    ),
    ("NGOs", _("NGOs")),
    # ("A_PUBLIC_BODIES", _("Public bodies")),
    # ("B_SOCIAL_CULTURAL", _("Social, cultural, educational bodies")),
    # ("C_PRIVATE_BODIES", _("Private bodies")),
    # ("D_NGOS", _("NGOs")),
    # ("E_OTHER", _("Other")),
]
eligible_entities_vocabulary = generic_vocabulary(_eligible_entities)
alsoProvides(eligible_entities_vocabulary, IVocabularyFactory)


_readiness_for_use = [
    ("A_TOOL_TESTED_IN_CASE_STUDIES", _("Tool tested in several case studies")),
    ("B_TOOL_BROADLY_USED", _("Tool broadly used")),
]
readiness_for_use_vocabulary = generic_vocabulary(_readiness_for_use)
alsoProvides(readiness_for_use_vocabulary, IVocabularyFactory)


_geographical_scale = [
    ("A_EUROPEAN", _("European")),
    ("B_NATIONAL", _("National")),
    ("C_REGIONAL", _("Regional")),
    ("D_MUNICIPAL_LOCAL", _("Municipal/Local")),
    ("E_BUILDING", _("Building")),
]
geographical_scale_vocabulary = generic_vocabulary(_geographical_scale)
alsoProvides(geographical_scale_vocabulary, IVocabularyFactory)


_tool_language = [
    ("Bulgarian", "Bulgarian"),
    ("Croatian", "Croatian"),
    ("Czech", "Czech"),
    ("Danish", "Danish"),
    ("Dutch", "Dutch"),
    ("English", "English"),
    ("Estonian", "Estonian"),
    ("Finnish", "Finnish"),
    ("French", "French"),
    ("German", "German"),
    ("Greek", "Greek"),
    ("Hungarian", "Hungarian"),
    ("Irish", "Irish"),
    ("Italian", "Italian"),
    ("Latvian", "Latvian"),
    ("Lithuanian", "Lithuanian"),
    ("Maltese", "Maltese"),
    ("Polish", "Polish"),
    ("Portuguese", "Portuguese"),
    ("Romanian", "Romanian"),
    ("Slovak", "Slovak"),
    ("Slovenian", "Slovenian"),
    ("Spanish", "Spanish"),
    ("Swedish", "Swedish"),
]
tool_language_vocabulary = generic_vocabulary(_tool_language)
alsoProvides(tool_language_vocabulary, IVocabularyFactory)


_most_useful_for = [
    ("RESEARCHER", _("Researcher")),
    ("REGIONAL_AUTHORITY", _("Staff of regional authority")),
    ("PRACTITIONERS", _("Practitioners at the regional level")),
    ("STAKEHOLDERS", _("Stakeholders")),
    ("CITIZEN", _("Citizen")),
]
most_useful_for_vocabulary = generic_vocabulary(_most_useful_for)
alsoProvides(most_useful_for_vocabulary, IVocabularyFactory)


_user_requirements = [
    ("A_BASIC", _("Basic")),
    ("B_ADVANCED", _("Advanced")),
    ("C_EXPERT", _("Expert")),
]
user_requirements_vocabulary = generic_vocabulary(_user_requirements)
alsoProvides(user_requirements_vocabulary, IVocabularyFactory)

budget_ranges = [
    "< 50.000 €",
    "50.000 - 100.000 €",
    "100.001 € - 1M €",
    "1M € - 10M €",
    "> 10M €",
]

budget_ranges_map = [
    ("lt50k", "< 50.000 €"),
    ("50k-100k", "50.000 - 100.000 €"),
    ("100k-1M", "100.001 € - 1M €"),
    ("1M-10M", "1M € - 10M €"),
    ("gt10M", "> 10M €"),
]

budget_ranges_reverse_map = {}
for token, label in budget_ranges_map:
    budget_ranges_reverse_map[label] = token

budget_ranges_vocabulary = generic_vocabulary(budget_ranges_map)
alsoProvides(budget_ranges_vocabulary, IVocabularyFactory)


type_of_funding = [
    "Grants",
    "Subsidies (or Prices)",
    "financial instruments & budgetary guarantees (e.g. loan, debt, guaranty and equity investment)",
    "Other",
]
type_of_funding_vocabulary = generic_vocabulary(type_of_funding)
alsoProvides(type_of_funding_vocabulary, IVocabularyFactory)

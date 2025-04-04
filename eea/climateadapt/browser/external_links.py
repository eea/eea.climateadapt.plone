# -*- coding: utf-8 -*-
import json
import logging

import requests
import transaction
import urllib.request, urllib.error, urllib.parse
from DateTime import DateTime
from eea.climateadapt._importer import utils as u
from lxml.etree import fromstring
from persistent.mapping import PersistentMapping
from plone import api
from plone.i18n.normalizer import idnormalizer
from html import unescape as html_unescape
from zope.annotation.interfaces import IAnnotations

from .admin import Item

# html_unescape = HTMLParser().unescape
logger = logging.getLogger('eea.climateadapt')


class DRMKCItem:
    def __init__(self, result):
        for attr in list(result.keys()):
            setattr(self, attr, result[attr])


class DRMKCImporter():
    def __init__(self, site):
        self.container = site['metadata']['projects']
        self.url = 'https://drmkc.jrc.ec.europa.eu/API/ProjectsExplorer/Query/Filter'
        self.payload = """{"Operator": "AND",
            "Rules": [ {
            "Property": "terms.fundingPrograms",
            "Value": "ENV-CLIMA",
            "Operator": "equals"
            }
            ],
            "Groups": [],
            "Aggregations": [],
            "Sorts": [ {
            "Property": "titleForSort.keyword",
            "Direction": "Asc"
            }
            ],
            "Start": 0,
            "Limit": 10,
            "Types": [
            "project"
            ]}"""
        self.headers = {'Content-type': 'application/json'}

    def get_response(self):
        response = requests.post(self.url, data=self.payload, headers=self.headers)
        return response.json()

    def create_obj(self, f, shortname, import_id):
        item = u.createAndPublishContentInContainer(
            self.container,
            'eea.climateadapt.aceproject',
            _publish=True,
            title=f.Title,
            long_description=u.t2r(f.Description),
            creation_date=DateTime(f.CreatedOnDate),
            acronym=f.Acronym,
            source='DRMKC',
            lead=f.CreatedByUser['DisplayName'],
            partners=u.t2r(''),
            sectors=[],
            climate_impacts=[],
            geochars='',
            rating=0,
            websites=()
            # f.Country,
            # f.EndDate,
            # f.ExternalIds,
            # f.Highlights,
            # f.Id,
            # f.LastModifiedByUser,
            # f.LastModifiedOnDate,
            # f.LengthInYears,
            # f.Location,
            # f.ModuleId,
            # f.NumCountries,
            # f.NumPartners,
            # f.NumPublications,
            # f.Organisations,
            # f.Publications,
            # f.StartDate,
            # f.TabId,
            # f.Terms,
            # f.Title,
            # f.TotalCost,
            # f.TotalCostPerYear,
            # f.TotalEcContribution,
            # f.TotalEcContributionPerYear,
            # f.Years,
            # f.Score
            # f.getGeoProperties
        )

        annot = IAnnotations(item)
        annot['import_id'] = import_id
        logger.warning('CREATING: %s', f.Title)
        return item

    def update_obj(self, f):
        item = self.update_content_in_container(
            self.container,
            'eea.climateadapt.aceproject',
            _publish=True,
            title=f.Title,
            long_description=u.t2r(f.Description),
            creation_date=DateTime(f.CreatedOnDate),
            acronym=f.Acronym,
            source='DRMKC',
            lead=f.CreatedByUser['DisplayName'],
            partners=u.t2r(''),
            sectors=[],
            climate_impacts=[],
            geochars='',
            rating=0,
            websites=()
            # rating= f.Score,
            # f.Country,
            # f.CreatedByUser,
            # f.EndDate,
            # f.ExternalIds,
            # f.Highlights,
            # f.Id,
            # f.LastModifiedByUser,
            # f.LastModifiedOnDate,
            # f.LengthInYears,
            # f.Location,
            # f.ModuleId,
            # f.NumCountries,
            # f.NumPartners,
            # f.NumPublications,
            # f.Organisations,
            # f.Publications,
            # f.StartDate,
            # f.TabId,
            # f.Terms,
            # f.Title,
            # f.TotalCost,
            # f.TotalCostPerYear,
            # f.TotalEcContribution,
            # f.TotalEcContributionPerYear,
            # f.Years,
            # f.getGeoProperties
        )

        logger.warning('UPDATING: %s. Last modified %s', obj.title, obj.modified())
        return item

    def update_content_in_container(self, shortname, *args, **kwargs):
        """Update content in projects database to match DRMKC data"""

        item = self.container[shortname]

        for attr in list(kwargs.keys()):
            setattr(item, attr, kwargs[attr])  # (object, name, value)

        item.reindexObject()
        item._p_changed = True

        return item

    def response_import(self, result):
        if not result['CreatedByUser']:  # edgecase when result['CreatedByUser'] is None
            result['CreatedByUser'] = {'DisplayName': ''}

        f = DRMKCItem(result)
        import_id = f.Id
        last_modified = DateTime(f.LastModifiedOnDate)
        shortname = idnormalizer.normalize(f.Title, None, 500)
        print(shortname)

        try:
            original = self.container[shortname]
        except KeyError:
            return self.create_obj(f, shortname, import_id)

        annot = getattr(original.aq_inner.aq_self, '__annotations__', {})
        test_id = annot.get('original_import_id')

        if (test_id == import_id) and (last_modified > original.modified()):
            return self.update_obj(f, shortname)
        else:
            if not hasattr(original.aq_inner.aq_self, '__annotations__'):
                original.__annotations__ = PersistentMapping()

            original.__annotations__['original_import_id'] = import_id
            raise NoUpdates

    def __call__(self):
        response = self.get_response()
        for result in response['Result']:
            try:
                obj = self.response_import(result)
            except NoUpdates:
                continue

        transaction.commit()


class NoUpdates(Exception):
    """ Already in database without modifications
    """
    pass


class AdapteCCACaseStudyImporter():
    """ Demo adaptecca importer
    """

    def __init__(self, site):
        self.case_studies_folder = site['metadata']['case-studies']

    def t_sectors(self, l):
        # Translate values to their CCA equivalent

        # TODO: check mapped ids
        # map = {
        #     u"Biodiversidad": "BIODIVERSITY",
        #     u"Recursos hídricos": "WATERMANAGEMENT",
        #     u"Bosques": "FORESTRY ",
        #     u"Sector agrario": "AGRICULTURE",
        #     # "Caza y pesca continental": "Inland hunting and fishing",
        #     # "Suelos y desertificación": "Soils and desertification",
        #     u"Transporte": "TRANSPORT",
        #     u"Salud humana": "HEALTH",
        #     # "Industria": "Industry",
        #     # "Turismo": "Tourism",
        #     u"Finanzas – Seguros": "FINANCIAL",
        #     u"Urbanismo y Construcción": "URBAN",
        #     u"Energía": "ENERGY",
        #     # "Sociedad": "Society",
        #     u"Zonas costeras": "COASTAL",
        #     # "Zonas de montaña": "Mountain zones",
        #     u"Medio marino y pesca": "MARINE",
        #     # "Ámbito Insular": "Islands",
        #     u"Medio Urbano": "URBAN",
        #     # "Medio Rural": "Rural environment",
        #     u"Eventos extremos": "DISASTERRISKREDUCTION",
        # }

        map = {
            "Water management": "WATERMANAGEMENT",
            "Ecosystem-based approaches (GI)": "ECOSYSTEM",
            "Urban": "URBAN",
            "Urban Planning and Construction": "URBAN",
            "Urban areas": "URBAN",
            "Disaster Risk Reduction": "DISASTERRISKREDUCTION",
            "Biodiversity": "BIODIVERSITY",
            "Coastal areas": "COASTAL",
            "BUILDINGS": "BUILDINGS",
            "Forestry": "FORESTRY ",
            "Forests": "FORESTRY ",
            "Agrarian sector": "AGRICULTURE",
            "Agriculture": "AGRICULTURE",
            "MARINE": "MARINE",
            "Financial": "FINANCIAL",
            "Energy": "ENERGY",
            "Transport": "TRANSPORT",
            "Health": "HEALTH",
            "Water resources": "WATERMANAGEMENT",

            "Rural areas": "Rural areas",
            "Transnational region (stretching across country borders)PORT": "Transnational region",

            "Transporte": "TRANSPORT",
        }

        return list(set([map.get(x, 'NONSPECIFIC') for x in l]))

    def t_impacts(self, l):
        # Translate values to their CCA equivalent

        # map = {
        #     u"Sequía / Escasez de agua": "DROUGHT",
        #     u"Eutrofización / salinización "
        #     u"/ pérdida de calidad de aguas continentales": "WATERSCARCE",
        #     u"Inundaciones": "FLOODING",
        #     # "Desertificación / Degradación forestal y de tierras"
        #     u"Aumento del nivel de mar": "SEALEVELRISE",
        #     u"Temperaturas extremas (olas de calor/frio)": "EXTREMETEMP",
        #     # "Impactos sobre la biodiversidad (fenología, distribución, etc.)"
        #     # "Impacts on biodiversity (phenology, distribution, etc.)",
        #     # "Enfermedades y vectores": "Illnesses and vectors",
        #     u"Vientos extraordinarios": "STORM",
        # }

        map = {
            "Flooding": "FLOODING",
            "Sea level rise": "SEALEVELRISE",
            "Ice and Snow": "ICEANDSNOW",
            "Extreme temperatures": "EXTREMETEMP",
            "Extreme temperature (heat and cold waves)": "EXTREMETEMP",
            "Storms": "STORM",
            "Drought": "DROUGHT",
            "Water Scarcity": "WATERSCARCE",
            "Desertification / Forest and land degradation": "DROUGHT",
        }

        return list(set([map.get(x, 'NONSPECIFIC') for x in l]))

    def html2text(self, html):
        if not isinstance(html, str):
            return ""
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        data = portal_transforms.convertTo('text/plain',
                                           html, mimetype='text/html')
        text = data.getData()

        return text.strip()

    def t_governance(self, level):
        # Translate values to their CCA equivalent
        # map = {
        #     u"Local": "LC",
        #     u"Regional": "SNA",
        #     u"Nacional": "NAT",
        #     u"Internacional": "TRANS",
        # }
        if level is None:
            return ''

        level = self.html2text(level)
        level = [x.strip() for x in level.split('\n')]

        map = {
            "Local": "LC",
            "Regional": "SNA",
            "Sub National Regions": "SNA",
            "National": "NAT",
            "Transnational region (stretching across country borders)": "TRANS",
        }

        # 'governance_level': ['LC', 'NAT', 'SNA'],
        return [map.get(x, '') for x in level]

    def t_geochars(self, v):
        # TODO: need to convert to geochar format
        # map = {
        #     u"Región Alpina": "TRANS_BIO_ALPINE",
        #     u"Región Atlántica": "TRANS_BIO_ATLANTIC",
        #     u"Región Mediterránea ": "TRANS_BIO_MEDIT",
        #     u"Región Macaronésica ": "TRANS_BIO_MACARO",
        # }

        map = {
            "Mediterranean": "TRANS_BIO_MEDIT",
            "Alpine": "TRANS_BIO_ALPINE",
            "Atlantic": "TRANS_BIO_ATLANTIC",
            "Pannonian": "TRANS_BIO_PANNONIAN",
            "Boreal": "TRANS_BIO_BOREAL",
            "Continental": "TRANS_BIO_CONTINENTAL",
            "Arctic": "TRANS_BIO_ARCTIC",
        }

        # TODO: is this a list or just a bio region?
        if type(v) is dict:
            return json.dumps(v)

        v = [x.strip() for x in v.split(',')]
        v = {"geoElements":
             {"element": "EUROPE", "macrotrans": None,
                 "biotrans": [map.get(x, '') for x in v], "countries": [],
                 "subnational": [], "city": "",
              }
             }
        return json.dumps(v)

    def update_content_in_container(self, shortname, *args, **kwargs):
        """Update content in case-studies to match AdapteCCA data"""

        item = self.case_studies_folder[shortname]

        for attr in list(kwargs.keys()):
            setattr(item, attr, kwargs[attr])  # (object, name, value)

        item.reindexObject()
        item._p_changed = True

        return item

    def node_import(self, container, node):
        f = Item(node)
        location = container
        import_id = f.item_id
        last_modified = DateTime(f.item_changed)
        shortname = idnormalizer.normalize(f.title, None, 500)

        try:
            original = location[shortname]
        except KeyError:
            return self.create_obj(location, f, import_id)

        annot = getattr(original.aq_inner.aq_self, '__annotations__', {})
        test_id = annot.get('original_import_id')

        if (test_id == import_id) and (last_modified > original.modified()):
            return self.update_obj(original, f, shortname)
        else:
            if not hasattr(original.aq_inner.aq_self, '__annotations__'):
                original.__annotations__ = PersistentMapping()

            original.__annotations__['original_import_id'] = import_id
            raise NoUpdates

    def create_obj(self, location, f, import_id):
        item = u.createAndPublishContentInContainer(
            location,
            'eea.climateadapt.casestudy',
            _publish=True,
            title=f.title,
            long_description=u.t2r(f.information),
            keywords=f.keywords.split(', '),
            sectors=self.t_sectors(f.sectors.split(', ')),
            climate_impacts=self.t_impacts(f.impact.split(', ')),
            governance_level=self.t_governance(f.governance),
            # regions
            geochars=self.t_geochars(f.regions),
            challenges=u.t2r(f.challenges),
            objectives=u.t2r(f.objectives),

            # in CCA this is a related items field
            # in AdapteCCA, these measures are linked concepts to other content
            # we'll ignore them for the time being?
            #
            # measures=self.to_terms(node.find('field_measures')),
            # adaptationoptions=measures,

            measure_type='A',       # it's a case study

            solutions=u.t2r(f.solutions),
            # f.adaptation
            # f.interest
            stakeholder_participation=u.t2r(f.stakeholder),
            success_limitations=u.t2r(f.factors),
            cost_benefit=u.t2r(f.budget),
            legal_aspects=u.t2r(f.legal),
            implementation_time=u.t2r(f.implementation),

            # TODO: there is no lifetime in AdapteCCA?

            contact=u.t2r(f.contact),
            websites=u.s2l(u.r2t(html_unescape(f.websites))) or [],

            # TODO: make sure we don't have paragraphs?
            source=u.r2t(f.sources),
            year=f.year,
            # images

            # TODO: in AdapteCCA, this is free text, we have 3 options
            # Select only one category below that best describes how relevant
            # this case study is to climate change adaptation
            # relevance=s2l(data.relevance),
            relevance=[],

            # comments=data.comments,
            # creation_date=creationdate,
            # effective_date=approvaldate,
            # elements=s2l(data.elements_),
            # geochars=data.geochars,
            # geolocation=geoloc,
            # implementation_type=data.implementationtype,
            # legal_aspects=t2r(data.legalaspects),
            # lifetime=t2r(data.lifetime),
            # primephoto=primephoto,
            # spatial_layer=data.spatiallayer,
            # spatial_values=s2l(data.spatialvalues),
            # supphotos=supphotos,

            origin_website='AdapteCCA',
        )

        annot = IAnnotations(item)
        annot['import_id'] = import_id
        logger.warning('CREATING: %s', f.title)
        return item

    def update_obj(self, obj, f, shortname):
        item = self.update_content_in_container(
            shortname,
            'eea.climateadapt.casestudy',
            _publish=True,
            title=f.title,
            long_description=u.t2r(f.information),
            keywords=f.keywords.split(', '),
            sectors=self.t_sectors(f.sectors.split(', ')),
            climate_impacts=self.t_impacts(f.impact.split(', ')),
            governance_level=self.t_governance(f.governance),
            geochars=self.t_geochars(f.regions),
            challenges=u.t2r(f.challenges),
            objectives=u.t2r(f.objectives),
            measure_type='A',       # it's a case study
            solutions=u.t2r(f.solutions),
            stakeholder_participation=u.t2r(f.stakeholder),
            success_limitations=u.t2r(f.factors),
            cost_benefit=u.t2r(f.budget),
            legal_aspects=u.t2r(f.legal),
            implementation_time=u.t2r(f.implementation),
            contact=u.t2r(f.contact),
            websites=u.s2l(u.r2t(html_unescape(f.websites))) or [],
            source=u.r2t(f.sources),
            year=f.year,
            relevance=[],
            origin_website='AdapteCCA',
        )

        logger.warning('UPDATING: %s. Last modified %s', obj.title, obj.modified())
        return item

    def __call__(self):
        response = urllib.request.urlopen('http://bio.devplx.com/adaptecca/cases_en.xml')
        AdapteCCA_data = response.read()
        e = fromstring(AdapteCCA_data)
        for node in e.xpath('//item'):
            try:
                item = self.node_import(self.case_studies_folder, node)
                transaction.commit()
            except NoUpdates:
                continue

            logger.warning(item.absolute_url())

        return 'AdapteCCA case study importer'

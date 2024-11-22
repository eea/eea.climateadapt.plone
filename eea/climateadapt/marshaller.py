import json
import logging

import pytz
import rdflib
import surf
from eea.climateadapt.interfaces import ICCACountry
from eea.climateadapt.vocabulary import (BIOREGIONS, SUBNATIONAL_REGIONS,
                                         ace_countries_dict)
from eea.rdfmarshaller.dexterity import Dexterity2Surf
from eea.rdfmarshaller.dexterity.fields import DXField2Surf
from eea.rdfmarshaller.interfaces import ISurfResourceModifier, ISurfSession
from eea.rdfmarshaller.value import Value2Surf
from plone.app.contenttypes.interfaces import ICollection
from plone.dexterity.interfaces import IDexterityContent
from plone.formwidget.geolocation.interfaces import IGeolocation
from plone.namedfile.interfaces import INamedBlobFile, INamedBlobImage
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import Interface, implements

from .vocabulary import ace_countries

logger = logging.getLogger("eea.climateadapt")
# from eea.climateadapt.catalog import macro_regions


class Collection2Surf(Dexterity2Surf):
    adapts(ICollection, ISurfSession)

    @property
    def blacklist_map(self):
        ptool = getToolByName(self.context, "portal_properties")
        props = getattr(ptool, "rdfmarshaller_properties", None)

        if props:
            blacklist = props.getProperty("blacklist") + ("query",)

            return list(
                props.getProperty("%s_blacklist" % self.portalType.lower(), blacklist)
            )
        else:
            self._blacklist.append("query")

            return self._blacklist


class GeoCharsFieldModifier(object):
    """Add geographic information to rdf export"""

    implements(ISurfResourceModifier)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """Change the rdf resource to include geochar terms"""

        if not hasattr(self.context, "geochars"):
            return

        value = self.context.geochars

        if not value:
            return ""

        value = json.loads(value)

        order = [
            "element",
            "macrotrans",
            "biotrans",
            "countries",
            "subnational",
            "city",
        ]

        spatial = []

        for key in order:
            element = value["geoElements"].get(key)

            if element:
                renderer = getattr(self, "_render_geochar_" + key)
                values = renderer(element).split(":")
                values[1] = values[1].split(",")
                values[1] = [x.strip() for x in values[1]]
                spatial += values[1]

                setattr(resource, "%s_%s" % ("eea", values[0]), values[1])
        setattr(resource, "dcterms_spatial", spatial)

    def _render_geochar_element(self, value):
        value = BIOREGIONS[value]

        return "region:{0}".format(value)

    def _render_geochar_macrotrans(self, value):
        tpl = "macro-transnational-region:{0}"

        return tpl.format(", ".join([BIOREGIONS[x] for x in value]))

    def _render_geochar_biotrans(self, value):
        tpl = "biographical-regions:{0}"

        return tpl.format(", ".join([BIOREGIONS.get(x, x) for x in value]))

    def _render_geochar_countries(self, value):
        tpl = "countries:{0}"
        value = [ace_countries_dict.get(x, x) for x in value]

        return tpl.format(", ".join(value))

    def _render_geochar_subnational(self, value):
        tpl = "sub-nationals:{0}"

        out = []

        for line in value:
            line = line.encode("utf-8")

            if line in SUBNATIONAL_REGIONS:
                out.append(SUBNATIONAL_REGIONS[line])

                continue
            else:
                logger.error("Subnational region not found: %s", line)

        text = ", ".join([x.decode("utf-8") for x in out])

        return tpl.format(text)

    def _render_geochar_city(self, value):
        text = value

        if isinstance(value, (list, tuple)):
            text = ", ".join(value)

        return "city:{0}".format(text)


class CountryTitle2Surf(DXField2Surf):
    """Override the country title to include more information"""

    adapts(Interface, ICCACountry, ISurfSession)

    def value(self):
        title = self.context.Title()

        if isinstance(title, str):
            title = title.encode("utf-8")

        return title + " - ClimateADAPT country profile"


class Geolocation2Surf(Value2Surf):
    """IValue2Surf implementation for plone.formwidget.Geolocation """

    adapts(IGeolocation)

    def __init__(self, value):
        self.value = value
        self.longitude = "longitude: %s" % value.longitude
        self.latitude = "latitude: %s" % value.latitude

    def __call__(self, *args, **kwds):
        return [self.longitude, self.latitude]


class File2Surf(Value2Surf):
    """IValue2Surf implementation for plone.namedfile.file.NamedBlobFile """

    adapts(INamedBlobFile)

    def __init__(self, value):
        self.value = value.filename


class Image2Surf(Value2Surf):
    """IValue2Surf implementation for plone.namedfile.file.NamedBlobImage """

    adapts(INamedBlobImage)

    def __init__(self, value):
        self.value = value.filename


class IssuedFieldModifier(object):
    """Add publishing information to rdf export"""

    implements(ISurfResourceModifier)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """Change the rdf resource to include issued term"""

        if not hasattr(self.context, "effective"):
            return

        value = self.context.effective().utcdatetime()

        timezone = pytz.timezone("UTC")
        utc_date = timezone.localize(value)
        value = rdflib.term.Literal(
            utc_date,
            datatype=rdflib.term.URIRef("http://www.w3.org/2001/XMLSchema#dateTime"),
        )
        setattr(resource, "dcterms_issued", value)
        setattr(resource, "eea_issued", value)


country_to_code = {v: k for k, v in ace_countries}


class CountryModifier(object):
    """Add publishing information to rdf export"""

    implements(ISurfResourceModifier)
    adapts(ICCACountry)

    def __init__(self, context):
        self.context = context

    def run(self, resource, adapter, session, **kwds):
        """Change the rdf resource to include issued term"""

        # <dcterms:spatial>
        # <geo:SpatialThing rdf:about="#geotag0">
        # <geo:long
        # rdf:datatype="http://www.w3.org/2001/XMLSchema#double">15.4749544</geo:long>
        # <geo:lat
        # rdf:datatype="http://www.w3.org/2001/XMLSchema#double">49.8167003</geo:lat>
        # <dcterms:type>administrative</dcterms:type>
        # <dcterms:title>Czechia</dcterms:title>
        # <rdfs:comment>Czechia</rdfs:comment>
        # <rdfs:label>Czechia</rdfs:label>
        # </geo:SpatialThing>
        # </dcterms:spatial>
        country = self.context.id.replace("-", " ").title()
        if country == 'Turkiye':
            country = 'Turkey'
        code = country_to_code[country]

        SpatialThing = session.get_class(surf.ns.GEO.SpatialThing)

        st = session.get_resource("#geotag-" + country, SpatialThing)
        st[surf.ns.DCTERMS["title"]] = country
        st[surf.ns.DCTERMS["type"]] = "administrative"
        st[surf.ns.RDFS["label"]] = country

        uri = "http://rdfdata.eionet.europa.eu/eea/countries/%s" % code
        st[surf.ns.OWL["sameAs"]] = rdflib.URIRef(uri)
        st.update()

        setattr(resource, "dcterms_spatial", st)


class ContributorModifier(object):
    """ Add contributor information to rdf export"""

    implements(ISurfResourceModifier)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def run(self, resource, adapter, session, **kwds):
        """Change the rdf resource to include issued term"""

        map_contributor_values = {
            "copernicus-climate-change-service-ecmw": "Copernicus Climate Change Service and Copernicus Atmosphere Monitoring Service",
            "european-centre-for-disease-prevention-and-control-ecdc": "European Centre for Disease Prevention and Control",
            "european-commission": "European Commission",
            "european-environment-agency-eea": "European Environment Agency",
            "european-food-safety-authority": "European Food Safety Authority",
            "lancet-countdown": "Lancet Countdown",
            "who-regional-office-for-europe-who-europe": "WHO Regional Office for Europe",
            "world-health-organization": "World Health Organization"
        }
        contributor_list = getattr(self.context, "contributor_list", None)

        if hasattr(self.context, 'include_in_observatory') and \
                self.context.include_in_observatory:

            partner_contributors = []
            if contributor_list:

                for contributor in contributor_list:
                    title = contributor.to_object.getId()

                    if title in map_contributor_values:
                        partner_contributors.append(map_contributor_values[title])
                    elif "Other Organisation" not in partner_contributors:
                        partner_contributors.append("Other Organisation")
            else:
                partner_contributors.append("Other Organisation")

            setattr(resource, "eea_partner_contributors", partner_contributors)


# class TransnationalRegionModifier():
#     implements(ISurfResourceModifier)
#     adapts(IDexterityContent)
#
#     def __init__(self, context):
#         self.context = context
#
#     def run(self, resource, *args, **kwds):
#         v = macro_regions(self.context)() or []
#         v = [BIOREGIONS[x] for x in v]
#
#         resource.eea_transnational_region = v

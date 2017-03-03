from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapts
from zope.interface import implements
from eea.climateadapt.vocabulary import BIOREGIONS
from eea.climateadapt.vocabulary import SUBNATIONAL_REGIONS
from eea.climateadapt.vocabulary import ace_countries_dict
import logging
import json
# import rdflib

logger = logging.getLogger('eea.climateadapt')


class GeoCharsFieldModifier(object):
    """Add geographic information to rdf export
    """

    implements(ISurfResourceModifier)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """Change the rdf resource to include geochar terms
        """
        if not hasattr(self.context, 'geochars'):
            return

        value = self.context.geochars
        if not value:
            return u""

        value = json.loads(value)

        order = ['element', 'macrotrans', 'biotrans',
                 'countries', 'subnational', 'city']

        for key in order:
            element = value['geoElements'].get(key)
            if element:
                renderer = getattr(self, "_render_geochar_" + key)
                values = renderer(element).split(':')
                setattr(resource, '%s_%s' % ("eea", values[0]),
                        [values[1]])

    def _render_geochar_element(self, value):
        value = BIOREGIONS[value]
        return u"region: {0}".format(value)

    def _render_geochar_macrotrans(self, value):
        tpl = u"macro-transnational-region: {0}"
        return tpl.format(u", ".join([BIOREGIONS[x] for x in value]))

    def _render_geochar_biotrans(self, value):
        tpl = u"biographical-regions:{0}"
        return tpl.format(u", ".join([BIOREGIONS.get(x, x) for x in value]))

    def _render_geochar_countries(self, value):
        tpl = u"countries:{0}"
        value = [ace_countries_dict.get(x, x) for x in value]
        return tpl.format(u", ".join(value))

    def _render_geochar_subnational(self, value):
        tpl = u"sub-nationals:{0}"

        out = []
        for line in value:
            line = line.encode('utf-8')
            if line in SUBNATIONAL_REGIONS:
                out.append(SUBNATIONAL_REGIONS[line])
                continue
            else:
                logger.error("Subnational region not found: %s", line)

        text = u", ".join([x.decode('utf-8') for x in out])
        return tpl.format(text)

    def _render_geochar_city(self, value):
        text = value
        if isinstance(value, (list, tuple)):
            text = u", ".join(value)
        return u"city:{0}".format(text)

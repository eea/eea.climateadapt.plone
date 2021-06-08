import json
import logging

from collective.cover.interfaces import ICover, ISearchableText
from eea.climateadapt.aceitem import IAceItem, IC3sIndicator
from eea.climateadapt.behaviors.aceproject import IAceProject
from eea.climateadapt.behaviors.adaptationoption import IAdaptationOption
from eea.climateadapt.behaviors.casestudy import ICaseStudy
from eea.climateadapt.city_profile import ICityProfile
from eea.climateadapt.interfaces import IClimateAdaptContent, INewsEventsLinks
from plone.api.portal import get_tool
from plone.indexer import indexer
from Products.CMFPlone.utils import safe_unicode
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.utils import get_stop_words
from zope.annotation.interfaces import IAnnotations
from zope.component import queryAdapter
from zope.interface import Interface

# from eea.climateadapt.browser.frontpage_slides import IRichImage
# from plone.rfc822.interfaces import IPrimaryFieldInfo

logger = logging.getLogger("eea.climateadapt")


@indexer(Interface)
def imported_ids(object):
    annot = IAnnotations(object).get("eea.climateadapt.imported_ids")

    if annot is None:
        return

    return list(annot)


@indexer(Interface)
def aceitem_id(object):
    if hasattr(object, "_aceitem_id"):
        return object._aceitem_id


@indexer(Interface)
def acemeasure_id(object):
    if hasattr(object, "_acemeasure_id"):
        return object._acemeasure_id


@indexer(Interface)
def aceproject_id(object):
    if hasattr(object, "_aceproject_id"):
        return object._aceproject_id


@indexer(Interface)
def countries(object):
    """Provides a list of countries this item "belongs" to

    We first look at the spatial_values attribute. If it doesn't exist, try to
    parse the geochars attribute
    """

    value = None

    if hasattr(object, "spatial_values"):
        value = object.spatial_values

    if value:
        # print "Return spatial values", object, value

        return value

    if hasattr(object, "geochars"):
        value = object.geochars

        if not value:
            return None

        value = json.loads(value)["geoElements"].get("countries", []) or None

        return value


@indexer(ICover)
def search_type(object):
    """"""

    return "CONTENT"


@indexer(INewsEventsLinks)
def search_type_for_newsevents(object):
    """"""

    return "CONTENT"


@indexer(ICityProfile)
def city_sectors(city):
    return city.key_vulnerable_adaptation_sector


@indexer(ICityProfile)
def city_climate_impacts(city):
    return city.climate_impacts_risks_particularly_for_city_region


@indexer(ICityProfile)
def city_stage_implementation_cycle(city):
    return city.stage_of_the_implementation_cycle


@indexer(ICityProfile)
def city_countries(city):
    return [city.country]


@indexer(ICityProfile)
def city_long_description(city):
    return ""


@indexer(IClimateAdaptContent)
def featured(obj):
    return obj.featured


@indexer(Interface)
def bio_regions(object):
    """Provides the list of bioregions, extracted from geochar"""

    value = None

    if hasattr(object, "geochars"):
        value = object.geochars

        if not value:
            return None

        value = json.loads(value)["geoElements"].get("biotrans", []) or None

        return value


@indexer(Interface)
def macro_regions(object):
    """Provides the list of macro_regions, extracted from geochar"""

    value = None

    if hasattr(object, "geochars"):
        value = object.geochars

        if not value:
            return None

        value = json.loads(value)["geoElements"].get("macrotrans", []) or None

        return value


def _get_aceitem_description(object):
    """Simplify the long description rich text in a simple 2 paragraphs
    "summary"
    """
    v = object.Description()

    if v:
        return v

    if not object.long_description:
        return ""

    text = object.long_description.raw
    portal_transforms = get_tool(name="portal_transforms")

    # Output here is a single <p> which contains <br /> for newline
    data = portal_transforms.convertTo("text/plain", text, mimetype="text/html")
    text = data.getData().strip()

    # the following is a very bad algorithm. Needs to use nltk.tokenize
    pars = text.split(".")

    return ".".join(pars[:2])

    return text


@indexer(IC3sIndicator)
def get_aceitem_description(object):
    return _get_aceitem_description(object)


@indexer(IAceItem)
def get_aceitem_description(object):
    return _get_aceitem_description(object)


@indexer(IAceProject)
def get_aceproject_description(object):
    return _get_aceitem_description(object)


@indexer(IAdaptationOption)
def get_adaptation_option_description(object):
    return _get_aceitem_description(object)


@indexer(ICaseStudy)
def get_casestudy_description(object):
    return _get_aceitem_description(object)


LANGUAGE = "english"
SENTENCES_COUNT = 2


@indexer(ICover)
def cover_description(obj):
    """Simplify the long description rich text in a simple 2 paragraphs
    "summary"
    """

    v = obj.Description()
    if v not in [None, ""]:
        return v

    portal_transforms = get_tool(name="portal_transforms")
    tiles = obj.get_tiles()
    text = []
    for tile in tiles:
        tile_obj = obj.restrictedTraverse("@@{0}/{1}".format(tile["type"], tile["id"]))

        searchable = queryAdapter(tile_obj, ISearchableText)
        if searchable:
            text.append(searchable.SearchableText())
        else:
            try:
                data = portal_transforms.convertTo(
                    "text/plain", tile_obj.getText(), mimetype="text/html"
                )
                text.append(data.getData().strip())
            except Exception:
                continue

    text = [safe_unicode(entry) for entry in text if entry]

    text = ".".join(text)
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))

    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    text = []
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        text.append(sentence._text)

    text = " ".join(text)
    # print("Description", text)
    return text

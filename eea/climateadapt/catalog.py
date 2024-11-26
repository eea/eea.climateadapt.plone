import json
import logging

from Acquisition import aq_base
# from collective.cover.interfaces import ICover, ISearchableText
from eea.climateadapt.aceitem import IAceItem, IC3sIndicator
from eea.climateadapt.behaviors.aceproject import IAceProject
from eea.climateadapt.behaviors.adaptationoption import IAdaptationOption
from eea.climateadapt.behaviors.casestudy import ICaseStudy
from eea.climateadapt.interfaces import IClimateAdaptContent, INewsEventsLinks
from plone.api.portal import get_tool
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
# from Products.CMFPlone.utils import safe_unicode
from zope.annotation.interfaces import IAnnotations
# from zope.component import queryAdapter
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


# @indexer(ICover)
# def search_type(object):
#     """"""

#     return "CONTENT"


@indexer(INewsEventsLinks)
def search_type_for_newsevents(object):
    """"""

    return "CONTENT"


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
    data = portal_transforms.convertTo(
        "text/plain", text, mimetype="text/html")
    text = data.getData().strip()

    # the following is a very bad algorithm. Needs to use nltk.tokenize
    pars = text.split(".")

    return ".".join(pars[:2])

    return text


@indexer(IC3sIndicator)
def get_aceitem_description_indicator(object):
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


# @indexer(ICover)
# def cover_description(obj):
#     """Simplify the long description rich text in a simple max 200 chars
#     "summary"
#     """

#     v = obj.Description()
#     if v not in [None, ""]:
#         return v

#     portal_transforms = get_tool(name="portal_transforms")
#     tiles = obj.get_tiles()
#     text = []
#     for tile in tiles:
#         # tile_obj = obj.unrestrictedTraverse(
#         # "@@{0}/{1}".format(tile["type"], tile["id"]))
#         tile_annot_id = "plone.tiles.data." + tile["id"]
#         tile_obj = obj.__annotations__.get(tile_annot_id, None)

#         searchable = queryAdapter(tile_obj, ISearchableText)
#         if searchable:
#             text.append(searchable.SearchableText())
#         else:
#             try:
#                 data = portal_transforms.convertTo(
#                     "text/plain", tile_obj["text"].raw, mimetype="text/html"
#                 )
#                 text.append(data.getData().strip())
#             except Exception:
#                 continue

#     text = [safe_unicode(entry) for entry in text if entry]

#     text = " ".join(text)
#     return text[:200]


@indexer(IDexterityContent)
def image_field_indexer(obj):
    """Indexer for knowing in a catalog search if a content has any image."""

    base_obj = aq_base(obj)

    image_field = ""
    if getattr(base_obj, "preview_image_link", False) \
        and not base_obj.preview_image_link.isBroken():
        image_field = 'preview_image'

    fields = ["preview_image", "image", "logo", "primary_photo"]

    for name in fields:
        if getattr(base_obj, name, False):
            image_field = name
            break

    return image_field

import json
import urllib.request
import urllib.parse
import urllib.error
import logging
from datetime import date

from DateTime import DateTime
from plone import api
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehaviorAssignable

from plone.namedfile.file import NamedBlobFile, NamedBlobImage, NamedFile, NamedImage
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.relation import RelationValue
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder

from .constants import LANGUAGE_INDEPENDENT_FIELDS

# from collective.cover.tiles.richtext import RichTextTile
# from plone.formwidget.geolocation.geolocation import Geolocation
# from eea.climateadapt.tiles.richtext import RichTextWithTitle
# from eea.climateadapt.translation import translate_one_text_to_translation_storage

logger = logging.getLogger("eea.climateadapt")


def translated_url(context, url, current_lang):
    """return the relative url for the object, including the current language
    example for FR

    /metadata/test -> /fr/metadata/test
    /en/metadata/test -> /fr/metadata/test
    """

    replace_urls = [
        "http://localhost:8080",
        "https://cca-p6.devel5cph.eionet.europa.eu",
        "https://cca.devel5cph.eionet.europa.eu",
        "https://climate-adapt.eea.europa.eu",
        "https://next-climate-adapt.eea.europa.eu",
    ]

    portal_url = context.portal_url()

    if portal_url in url:
        relative_path = url.replace(portal_url, "")
    else:
        for r_url in replace_urls:
            url = url.replace(r_url, "")

        relative_path = url

    if relative_path.startswith("/"):
        relative_path = relative_path[1:]

    if relative_path.startswith("http"):
        logger.warn("Didn't convert translated url %s", url)
        return url

    relative_path_split = relative_path.split("/")

    if relative_path_split[0] == current_lang:
        return relative_path

    if relative_path_split[0] == "en":
        new_path = "/{}/{}".format(current_lang, "/".join(relative_path_split[1:]))

        return new_path

    new_path = "/{}/{}".format(current_lang, relative_path)

    return new_path


class TranslationUtilsMixin(object):
    """Class with utility methods related to translations"""

    def translated_url(self, url):
        return translated_url(self.context, url, self.current_lang)

    def translated_object(self, object):
        url = object.absolute_url()
        """return the relative url for the object, including the current language
        example for FR

        /metadata/test -> /fr/metadata/test
        /en/metadata/test -> /fr/metadata/test
        """

        replace_urls = [
            "https://cca.devel5cph.eionet.europa.eu",
            "https://climate-adapt.eea.europa.eu",
        ]

        portal_url = self.context.portal_url()

        if portal_url in url:
            relative_path = url.replace(portal_url, "")
        else:
            for r_url in replace_urls:
                url = url.replace(r_url, "")

            relative_path = url

        if relative_path.startswith("/"):
            relative_path = relative_path[1:]

        relative_path_split = relative_path.split("/")

        if relative_path_split[0] == self.current_lang:
            return relative_path

        if relative_path_split[0] == "en":
            new_path = "/{}/{}".format(
                self.current_lang, "/".join(relative_path_split[1:])
            )

        try:
            site = api.portal.get()
            object = site.restrictedTraverse("/cca" + new_path)
        except:
            object = None

        return object

    @property
    def current_lang(self):
        current_language = get_current_language(self.context, self.request)

        return current_language

    # def get_translation_for_text(self, value, language=None):
    #     if not language:
    #         language = self.current_lang
    #
    #     language = language.upper()
    #
    #     if language == "EN":
    #         return value
    #
    #     translated = translate_one_text_to_translation_storage("EN", value, [language])
    #
    #     if "translated" in translated:
    #         encoded_text = translated["transId"].encode("latin-1")
    #
    #         return encoded_text
    #
    #     return value

    def get_i18n_for_text(self, text, domain="eea.climateadapt", language=None):
        if not language:
            language = self.current_lang

        language = language.lower()

        if language == "en":
            return text

        return translate_text(self.context, self.request, text, domain, language)


def get_current_language(context, request):
    try:
        context = context.aq_inner
        portal_state = getMultiAdapter((context, request), name="plone_portal_state")
        return portal_state.language()
    except Exception:
        return "en"


def translate_text(context, request, text, domain="eea.climateadapt", language=None):
    tool = getToolByName(context, "translation_service")
    if not language:
        language = get_current_language(context, request)

    return tool.translate(text, domain=domain, target_language=language)


def get_site_languages():
    try:
        languages = list(
            TranslationManager(api.portal.get().restrictedTraverse("en"))
            .get_translations()
            .keys()
        )
        return languages
    except Exception:
        return []


def filters_to_query(args):
    """

    args = [
        ('objectProvides', ACEID_TO_SEARCHTYPE.get(search_type) or search_type),
        ('cca_adaptation_sectors.keyword', "Urban"),
    ]
    """
    res = []
    for i, (name, val) in enumerate(args):
        if name == "q":
            if isinstance(val, list):
                val = val[0]
            res.append([name, val])
            continue
        res.append(["filters[{0}][field]".format(i), name])
        res.append(["filters[{0}][type]".format(i), "any"])
        if isinstance(val, list):
            for x, lv in enumerate(val):
                res.append(["filters[{0}][values][{1}]".format(i, x), lv])
        else:
            res.append(["filters[{0}][values][0]".format(i), val])

    return urllib.parse.urlencode(dict(res))


def get_object_fields(obj):
    behavior_assignable = IBehaviorAssignable(obj)
    fields = {}
    if behavior_assignable:
        behaviors = behavior_assignable.enumerateBehaviors()
        for behavior in behaviors:
            for k, v in getFieldsInOrder(behavior.interface):
                fields.update({k: v})
    for k, v in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
        fields.update({k: v})
    return fields


def is_language_independent_value(value):
    if (
        isinstance(value, bool)
        or isinstance(value, int)
        or isinstance(value, tuple)
        or isinstance(value, list)
        or isinstance(value, set)
        or isinstance(value, dict)
        or isinstance(value, NamedBlobImage)
        or isinstance(value, NamedBlobFile)
        or isinstance(value, NamedImage)
        or isinstance(value, NamedFile)
        or isinstance(value, DateTime)
        or isinstance(value, date)
        or isinstance(value, RelationValue)
        # or isinstance(value, Geolocation)
    ):
        return True
    return False


def is_json(input):
    try:
        json.loads(input)
    except ValueError as e:
        return False
    return True


def get_object_fields_values(obj):
    # TODO: perhaps a list by each portal_type
    tile_fields = ["title", "text", "description", "tile_title", "footer", "alt_text"]

    data = {
        "portal_type": obj.portal_type,
        "path": obj.absolute_url(),
        "item": {},
        "html": {},
        "tile": {},
    }

    # get tile data
    # if obj.portal_type == "collective.cover.content":
    #     tiles_id = obj.list_tiles()
    #     for tile_id in tiles_id:
    #         data["tile"][tile_id] = {"item": {}, "html": {}}
    #         tile = obj.get_tile(tile_id)
    #         for field in tile_fields:
    #             value = None
    #             if isinstance(tile, RichTextWithTitle) or isinstance(
    #                 tile, RichTextTile
    #             ):
    #                 if field in tile_fields:
    #                     try:
    #                         if isinstance(tile.data.get(field), RichTextValue):
    #                             value = tile.data.get(field).raw
    #                             if value:
    #                                 data["tile"][tile_id]["html"][field] = value
    #                         else:
    #                             value = tile.data.get(field)
    #                             if value:
    #                                 data["tile"][tile_id]["item"][field] = value
    #                     except Exception:
    #                         value = None
    #             else:
    #                 value = tile.data.get(field, None)
    #                 if value:
    #                     data["tile"][tile_id]["item"][field] = value

    skip_fields = [
        "acronym",
        "id",
        "language",
        "portal_type",
        "contentType",
    ] + LANGUAGE_INDEPENDENT_FIELDS

    fields = get_object_fields(obj)
    for key in fields:
        if key in skip_fields:
            continue

        raw_value = getattr(obj, key)
        value = getattr(raw_value, "raw", getattr(obj, key))

        if not value:
            continue

        # ignore some value types
        if is_language_independent_value(value):
            continue

        if callable(value):
            # ignore datetimes
            if isinstance(value(), DateTime):
                continue

            value = value()

        if isinstance(raw_value, RichTextValue):
            value = raw_value.raw.replace("\r\n", "")
            data["html"][key] = value
            continue

        if is_json(value):
            continue

        data["item"][key] = value

    return data


def get_value_representation(obj, name):
    """Returns a value suitable for representation in HTML"""
    value = getattr(obj, name)

    if is_language_independent_value(value):
        return None

    if callable(value):
        value = value()

        # TODO: we should not need to do this
        if isinstance(value, DateTime):  # ignore datetimes
            return None

    if isinstance(value, RichTextValue):
        if value.raw:
            value = value.raw.replace("\r\n", "")
        else:
            value = ""

    # if is_json(value):
    #     return None

    return value

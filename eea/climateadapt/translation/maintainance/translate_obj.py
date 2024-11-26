import logging

# from collective.cover.tiles.richtext import RichTextTile
from DateTime import DateTime
from plone.api import portal
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehaviorAssignable
from zope.schema import getFieldsInOrder

from eea.climateadapt.browser.admin import force_unlock
from eea.climateadapt.tiles.richtext import RichTextWithTitle
from eea.climateadapt.translation import (
    retrieve_html_translation,
    translate_one_field_in_one_step,
    translate_one_text_to_translation_storage,
)
from eea.climateadapt.translation.constants import (
    IGNORE_FIELDS,
    LANGUAGE_INDEPENDENT_FIELDS,
    cca_event_languages,
    source_richtext_types,
    tile_fields,
)
from eea.climateadapt.translation.utils import (
    get_object_fields_values,
    is_language_independent_value,
)

from ..utils import is_json

logger = logging.getLogger("eea.climateadapt")


def get_language_for_obj(obj, default_lang):
    source_language = default_lang

    if obj.portal_type == "cca-event":
        custom_language = obj.event_language
        if custom_language is not None:
            custom_language = cca_event_languages.get(custom_language, None)
            if custom_language is not None:
                source_language = custom_language

    return source_language


def get_object_fields(obj):
    # get behavior fields and values
    behavior_assignable = IBehaviorAssignable(obj)
    fields = {}
    if behavior_assignable:
        behaviors = behavior_assignable.enumerateBehaviors()
        for behavior in behaviors:
            for k, v in getFieldsInOrder(behavior.interface):
                fields.update({k: v})

    #  get schema fields and values
    for k, v in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
        fields.update({k: v})

    return fields


def handle_cover_one_step(trans_obj, obj_en, language, source_language, trans_obj_path):
    json_data = get_object_fields_values(obj_en)

    tile_html_fields = []
    if "tile" in json_data:
        for tile_id in list(json_data["tile"].keys()):
            tile_data = json_data["tile"][tile_id]
            # LOOP tile text items
            for key in list(tile_data["item"].keys()):
                # TODO add one step params
                res = translate_one_field_in_one_step(
                    source_language,
                    tile_data["item"][key],
                    [language.upper()],
                    uid=trans_obj.UID(),
                    obj_path=trans_obj_path,
                    field=key,
                    tile_data=tile_data,
                    tile_id=tile_id,
                )
                logger.info("One step translation tile: %s", res)
            # LOOP tile HTML items
            for key in list(tile_data["html"].keys()):
                value = tile_data["html"][key]
                value = value.replace("\r", "")
                value = value.replace("\n", "")
                try:
                    _ = value + "test"
                except UnicodeDecodeError:
                    value = value.decode("utf-8")
                tile_html_fields.append(
                    {"tile_id": tile_id, "field": key, "value": value}
                )

    # Translate simple fields
    for key in list(json_data["item"].keys()):
        res = translate_one_field_in_one_step(
            source_language,
            json_data["item"][key],
            [language.upper()],
            uid=trans_obj.UID(),
            obj_path=trans_obj_path,
            field=key,
        )

    # TILE HTML fields translate in one call
    if len(tile_html_fields):
        if not trans_obj_path:
            return

        html_content = "<!doctype html>" + "<head><meta charset=utf-8></head><body>"
        for item in tile_html_fields:
            html_tile = get_html_field(item["field"], item["tile_id"], item["value"])
            html_content += html_tile

        html_content += "</body></html>"
        html_content = html_content.encode("utf-8")

        retrieve_html_translation(
            source_language,
            html_content,
            trans_obj_path,
            language.upper(),
        )


def get_html_field(field, tile_id, value):
    return (
        "<div class='cca-translation-tile' data-field='%s' data-tile-id='%s'>%s</div>"
        % (field, tile_id, value)
    )


def handle_cover(trans_obj, language, source_language, trans_obj_path):
    tiles_id = trans_obj.list_tiles()

    for tile_id in tiles_id:
        tile = trans_obj.get_tile(tile_id)
        for field in tile_fields:
            value = tile.data.get(field)
            if value:
                translated = (
                    translate_one_text_to_translation_storage(
                        source_language, value, [language.upper()]
                    )
                    or {}
                )

                if "translated" in translated:
                    encoded_text = translated["transId"].encode("latin-1")
                    tile.data.update({field: encoded_text})

        if isinstance(tile, RichTextWithTitle):  # or isinstance(tile, RichTextTile):
            try:
                value = tile.data.get("text").raw
            except Exception:
                value = None
            if value:
                html_content = (
                    "<!doctype html>" + "<head><meta charset=utf-8></head><body>"
                )

                value = value.replace("\r", "")
                value = value.replace("\n", "")
                try:
                    _ = value + "test"
                except UnicodeDecodeError:
                    value = value.decode("utf-8")
                html_tile = get_html_field("no_value", tile_id, value)

                html_content += html_tile

                html_content += "</body></html>"
                html_content = html_content.encode("utf-8")
                translated = retrieve_html_translation(
                    source_language,
                    html_content,
                    trans_obj_path,
                    language.upper(),
                )

                if translated and "translated" in translated:
                    try:
                        encoded_text = translated["transId"].encode("latin-1")
                        tile.data["text"].raw = encoded_text
                    except AttributeError:
                        logger.info("Error for tile. TODO improve.")
                        logger.info(tile_id)


def get_translation_object(trans_obj, obj_en, obj, version):
    layout_en = obj_en.getLayout()
    default_view_en = obj_en.getDefaultPage()
    layout_default_view_en = None
    if default_view_en is not None:
        layout_default_view_en = obj_en[default_view_en].getLayout()

    if not hasattr(trans_obj, "REQUEST"):
        trans_obj.REQUEST = obj.REQUEST

    if version is not None:
        obj_version = int(getattr(trans_obj, "version", 0))

        if obj_version >= version:
            logger.info("Skipping! object already at version %s", obj_version)
            return None

        trans_obj.version = version

    # set the layout of the translated object to match the english object
    trans_obj.setLayout(layout_en)

    # also set the layout of the default view
    if default_view_en and layout_default_view_en:
        trans_obj[default_view_en].setLayout(layout_default_view_en)

    return trans_obj


def translate_obj(obj, lang=None, version=None, one_step=False):
    """Translate given obj. Use one_step = True to translate in a single step
    without using annotations.
    """
    source_language = get_language_for_obj(obj, "EN")
    force_unlock(obj)

    fields = get_object_fields(obj)

    translations = TranslationManager(obj).get_translations()
    obj_en = translations.pop("en")

    if not hasattr(obj_en, "REQUEST"):
        obj_en.REQUEST = obj.REQUEST

    dummy = {"errors": []}

    if lang is None:
        return dummy

    for language in translations:
        if language != lang:
            continue

        trans_obj = get_translation_object(translations[language], obj_en, obj, version)

        if trans_obj is not None:
            translate_obj_with_language(
                trans_obj, obj, obj_en, fields, language, source_language, one_step
            )

    return dummy


def translatable_fields(trans_obj, fields):
    res = []
    for fieldname in fields:
        if fieldname in IGNORE_FIELDS + LANGUAGE_INDEPENDENT_FIELDS:
            continue

        # if trans_obj.portal_type in ["Event", "cca-event"]:
        #     if fieldname in ["start", "end", "timezone"]:
        #         continue

        res.append(fieldname)

    return res


def get_value(obj, fieldname):
    raw_value = getattr(obj, fieldname)

    is_richtext = hasattr(raw_value, "raw")
    value = getattr(raw_value, "raw", raw_value)

    if not value:
        return None

    if callable(value):
        if isinstance(value(), DateTime):  # ignore datetimes
            return None

        value = value()

    # ignore some value types
    if is_language_independent_value(value):
        return None

    if isinstance(getattr(obj, fieldname), RichTextValue):
        value = getattr(obj, fieldname).raw.replace("\r\n", "")

    if is_json(value):
        return None

    return (value, is_richtext)


def translate_obj_with_language(
    trans_obj, obj, obj_en, fields, language, source_language, one_step
):
    site_url = portal.getSite().absolute_url()

    trans_obj_url = trans_obj.absolute_url()
    trans_obj_path = "/cca" + trans_obj_url.split(site_url)[-1]

    # get tile data
    if trans_obj.portal_type == "collective.cover.content":
        if one_step is True:
            # One step translation for covers/tiles
            handle_cover_one_step(
                trans_obj, obj_en, language, source_language, trans_obj_path
            )
        else:
            handle_cover(trans_obj, language, source_language, trans_obj_path)

    # send requests to translation service for each field
    # update field in obj
    rich_fields = set()

    reindex = []
    for fieldname in translatable_fields(trans_obj, fields):
        bits = get_value(obj, fieldname)

        if bits is None:
            continue

        value, is_rich_field = bits

        if not value:
            continue

        if is_rich_field:
            rich_fields.add(fieldname)

        force_unlock(trans_obj)

        if one_step and fieldname not in rich_fields:  # shortcuts the circuit
            translate_one_field_in_one_step(
                source_language,
                value,
                [language.upper()],
                uid=trans_obj.UID(),
                obj_path=trans_obj_path,
                field=fieldname,
            )
            continue

        translated = (
            translate_one_text_to_translation_storage(
                source_language, value, [language.upper()]
            )
            or {}
        )
        if "translated" in translated:
            # TODO improve this part, after no more errors
            encoded_text = translated["transId"].encode("latin-1")

            if fieldname == "source" and obj.portal_type in source_richtext_types:
                setattr(trans_obj, fieldname, RichTextValue(encoded_text))

                trans_obj._p_changed = True
                reindex.append(fieldname)
                continue

            if fieldname not in rich_fields:
                setattr(trans_obj, fieldname, encoded_text)

            trans_obj._p_changed = True
            reindex.append(fieldname)

    if reindex:
        trans_obj.reindexObject(idxs=reindex)

    if len(rich_fields) > 0:
        handle_obj_with_richfields(
            obj, list(rich_fields), source_language, trans_obj_path, language
        )


def handle_obj_with_richfields(
    obj, rich_fields, source_language, trans_obj_path, language
):
    html_content = "<!doctype html><head><meta charset=utf-8></head>"
    html_content += "<body>"

    for key in rich_fields:
        value = getattr(obj, key).raw.replace("\r\n", "")
        html_section = (
            "<div class='cca-translation-section'"
            + " data-field='"
            + key
            + "'>"
            + value
            + "</div>"
        )

        html_content += html_section

    html_content += "</body></html>"
    html_content = html_content.encode("utf-8")
    retrieve_html_translation(
        source_language,
        html_content,
        trans_obj_path,
        language.upper(),
    )

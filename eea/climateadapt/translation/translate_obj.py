from plone.app.textfield.value import RichTextValue
from DateTime import DateTime
import logging
from zope.schema import getFieldsInOrder
from eea.climateadapt.browser.admin import force_unlock
from plone.app.multilingual.manager import TranslationManager
from plone.api import portal
from plone.behavior.interfaces import IBehaviorAssignable
from eea.climateadapt.translation import (
    retrieve_html_translation,
    retrieve_translation,
    retrieve_translation_one_step,
)
from eea.climateadapt.translation.constants import (
    cca_event_languages,
    LANGUAGE_INDEPENDENT_FIELDS,
    source_richtext_types,
)
from eea.climateadapt.translation.utils import get_object_fields_values
from eea.climateadapt.translation.utils import is_language_independent_value
from collective.cover.tiles.richtext import RichTextTile
from eea.climateadapt.tiles.richtext import RichTextWithTitle
from .utils import is_json

logger = logging.getLogger("eea.climateadapt")


def translate_obj(obj, lang=None, version=None, one_step=False):
    """Translate given obj. Use one_step = True to translate in a single step
    without using annotations.
    """
    # import pdb; pdb.set_trace()
    source_language = "EN"
    tile_fields = ["title", "description", "tile_title", "footer", "alt_text"]
    errors = []
    force_unlock(obj)

    site_url = portal.getSite().absolute_url()
    # obj_url = obj.absolute_url()
    # obj_path = "/cca" + obj_url.split(site_url)[-1]

    if obj.portal_type == "cca-event":
        custom_language = obj.event_language
        if custom_language is not None:
            custom_language = cca_event_languages.get(custom_language, None)
            if custom_language is not None:
                source_language = custom_language

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

    translations = TranslationManager(obj).get_translations()
    obj_en = translations.pop("en")

    if not hasattr(obj_en, "REQUEST"):
        obj_en.REQUEST = obj.REQUEST

    layout_en = obj_en.getLayout()
    default_view_en = obj_en.getDefaultPage()
    layout_default_view_en = None
    if default_view_en is not None:
        layout_default_view_en = obj_en[default_view_en].getLayout()

    for language in translations:
        if lang is not None:
            if language != lang:
                continue

        trans_obj = translations[language]
        trans_obj_url = trans_obj.absolute_url()
        trans_obj_path = "/cca" + trans_obj_url.split(site_url)[-1]

        if not hasattr(trans_obj, "REQUEST"):
            trans_obj.REQUEST = obj.REQUEST

        if version is not None:
            obj_version = int(getattr(trans_obj, "version", 0))

            if obj_version >= version:
                logger.info("Skipping! object already at version %s", obj_version)
                continue

            trans_obj.version = version

        # set the layout of the translated object to match the english object
        trans_obj.setLayout(layout_en)

        # also set the layout of the default view
        if default_view_en and layout_default_view_en:
            trans_obj[default_view_en].setLayout(layout_default_view_en)

        # get tile data
        if trans_obj.portal_type == "collective.cover.content" and one_step is True:
            # One step translation for covers/tiles
            json_data = get_object_fields_values(obj_en)

            tile_html_fields = []
            if "tile" in json_data:
                for tile_id in json_data["tile"].keys():
                    tile_data = json_data["tile"][tile_id]
                    # LOOP tile text items
                    for key in tile_data["item"].keys():
                        # TODO add one step params
                        res = retrieve_translation_one_step(
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
                    for key in tile_data["html"].keys():
                        value = tile_data["html"][key]
                        value = value.replace("\r", "")
                        value = value.replace("\n", "")
                        try:
                            test_value = value + "test"
                        except UnicodeDecodeError:
                            value = value.decode("utf-8")
                        tile_html_fields.append(
                            {"tile_id": tile_id, "field": key, "value": value}
                        )

            # Translate simple fields
            for key in json_data["item"].keys():
                res = retrieve_translation_one_step(
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
                    continue
                html_content = (
                    "<!doctype html>" + "<head><meta charset=utf-8></head><body>"
                )
                for item in tile_html_fields:
                    html_tile = (
                        "<div class='cca-translation-tile'"
                        + " data-field='"
                        + item["field"]
                        + "'"
                        + " data-tile-id='"
                        + item["tile_id"]
                        + "'"
                        + ">"
                        + item["value"]
                        + "</div>"
                    )
                    html_content += html_tile

                html_content += "</body></html>"
                html_content = html_content.encode("utf-8")
                translated = retrieve_html_translation(
                    source_language,
                    html_content,
                    trans_obj_path,
                    language.upper(),
                    False,
                )
        elif trans_obj.portal_type == "collective.cover.content":
            tiles_id = trans_obj.list_tiles()

            for tile_id in tiles_id:
                tile = trans_obj.get_tile(tile_id)
                for field in tile_fields:
                    value = tile.data.get(field)
                    if value:
                        translated = (
                            retrieve_translation(
                                source_language, value, [language.upper()]
                            )
                            or {}
                        )

                        if "translated" in translated:
                            encoded_text = translated["transId"].encode("latin-1")
                            tile.data.update({field: encoded_text})

                if isinstance(tile, RichTextWithTitle) or isinstance(
                    tile, RichTextTile
                ):
                    try:
                        value = tile.data.get("text").raw
                    except Exception:
                        value = None
                    if value:
                        html_content = (
                            "<!doctype html>"
                            + "<head><meta charset=utf-8></head><body>"
                        )

                        value = value.replace("\r", "")
                        value = value.replace("\n", "")
                        try:
                            test_value = value + "test"
                        except UnicodeDecodeError:
                            value = value.decode("utf-8")
                        html_tile = (
                            "<div class='cca-translation-tile'"
                            + " data-field='"
                            + field
                            + "'"
                            + " data-tile-id='"
                            + tile_id
                            + "'"
                            + ">"
                            + value
                            + "</div>"
                        )

                        html_content += html_tile

                        html_content += "</body></html>"
                        html_content = html_content.encode("utf-8")
                        translated = retrieve_html_translation(
                            source_language,
                            html_content,
                            trans_obj_path,
                            language.upper(),
                            False,
                        )

                        if "translated" in translated:
                            try:
                                encoded_text = translated["transId"].encode("latin-1")
                                tile.data["text"].raw = encoded_text
                            except AttributeError:
                                logger.info("Error for tile. TODO improve.")
                                logger.info(tile_id)

        # send requests to translation service for each field
        # update field in obj
        rich_fields = []

        for key in fields:
            rich = False
            # print(key)
            if key in ["acronym", "id", "language", "portal_type", "contentType"]:
                continue
            if key in LANGUAGE_INDEPENDENT_FIELDS:
                continue

            value = getattr(getattr(obj, key), "raw", getattr(obj, key))

            if trans_obj.portal_type in ["Event", "cca-event"]:
                if key in ["start", "end", "timezone"]:
                    continue

            if not value:
                continue

            if callable(value):
                # ignore datetimes
                if isinstance(value(), DateTime):
                    continue

                value = value()

            # ignore some value types
            if is_language_independent_value(value):
                continue

            if isinstance(getattr(obj, key), RichTextValue):
                value = getattr(obj, key).raw.replace("\r\n", "")
                rich = True
                if key not in rich_fields:
                    rich_fields.append(key)

            if is_json(value):
                continue

            if key not in errors:
                errors.append(key)
            force_unlock(trans_obj)

            if one_step is True and rich is not True:
                translated = retrieve_translation_one_step(
                    source_language,
                    value,
                    [language.upper()],
                    uid=trans_obj.UID(),
                    obj_path=trans_obj_path,
                    field=key,
                )
                continue

            translated = (
                retrieve_translation(source_language, value, [language.upper()]) or {}
            )
            if "translated" in translated:
                # TODO improve this part, after no more errors
                encoded_text = translated["transId"].encode("latin-1")

                if key == "source" and obj.portal_type in source_richtext_types:
                    # import pdb; pdb.set_trace()
                    setattr(trans_obj, key, getattr(obj, key))
                    # setattr(trans_obj, key, encoded_text)
                    # setattr(trans_obj, key, translated['transId'])

                    setattr(trans_obj, key, RichTextValue(encoded_text))
                    # ValueError: Can not convert 'Elsevier' to an IRichTextValue
                    # <ResearchProject at /cca/ro/help/share-your-info/research-and-knowledge-projects
                    # /elderly-resident2019s-uses-of-and-preferences-for-urban-green-spaces-during-hea
                    # t-periods>

                    # reindex object
                    trans_obj._p_changed = True
                    trans_obj.reindexObject(idxs=[key])
                    continue

                if rich:
                    pass
                    # TODO No action needed, right?
                    # setattr(trans_obj, key, getattr(obj, key))
                    # setattr(trans_obj, key, RichTextValue(encoded_text))
                    # setattr(getattr(trans_obj, key), 'raw', encoded_text)
                else:
                    setattr(trans_obj, key, encoded_text)

                # reindex object
                trans_obj._p_changed = True
                trans_obj.reindexObject(idxs=[key])

        if len(rich_fields) > 0:
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
            res = retrieve_html_translation(
                source_language,
                html_content,
                trans_obj_path,
                language.upper(),
                False,
            )

    return {"errors": errors}

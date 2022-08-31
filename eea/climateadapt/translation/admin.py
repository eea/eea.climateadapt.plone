""" Admin translation
"""
import json
import logging
import os
import time
from collections import defaultdict
from datetime import date, datetime
from DateTime import DateTime
import transaction

from collective.cover.tiles.richtext import RichTextTile
from plone import api
from plone.api import content, portal
from plone.api.content import get_state
from plone.app.layout.viewlets import ViewletBase
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from plone.api.portal import get_tool
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.behavior.interfaces import IBehaviorAssignable
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from plone.namedfile.file import NamedFile, NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from z3c.relationfield.relation import RelationValue
from Products.Five.browser import BrowserView

from eea.climateadapt.browser.admin import force_unlock
from eea.climateadapt.tiles.richtext import RichTextWithTitle
from eea.climateadapt.translation import retrieve_translation
from eea.climateadapt.translation import retrieve_translation_one_step
from eea.climateadapt.translation import retrieve_html_translation
from eea.climateadapt.translation import get_translated
from eea.climateadapt.translation.utils import get_current_language
from eea.climateadapt.translation.utils import translate_text

from zope.schema import getFieldsInOrder
from zope.site.hooks import getSite

logger = logging.getLogger('eea.climateadapt')


def is_json(input):
    try:
        json.loads(input)
    except ValueError as e:
        return False
    return True


def translate_obj(obj, lang=None, version=None, one_step=False):
    """ Translate given obj. Use one_step = True to translate in a single step
        without using annotations.
    """
    tile_fields = ['title', 'description', 'tile_title', 'footer', 'alt_text']
    errors = []
    force_unlock(obj)

    site_url = portal.getSite().absolute_url()
    obj_url = obj.absolute_url()
    obj_path = '/cca' + obj_url.split(site_url)[-1]

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
    obj_en = translations.pop('en')
    layout_en = obj_en.getLayout()
    default_view_en = obj_en.getDefaultPage()
    if default_view_en is not None:
        layout_default_view_en = obj_en[default_view_en].getLayout()

    for language in translations:
        if lang is not None:
            if language != lang:
                continue

        trans_obj = translations[language]
        trans_obj_url = trans_obj.absolute_url()
        trans_obj_path = '/cca' + trans_obj_url.split(site_url)[-1]

        if version is not None:
            obj_version = int(getattr(trans_obj, 'version', 0))

            if obj_version >= version:
                logger.info(
                    "Skipping! object already at version %s", obj_version)
                continue

            trans_obj.version = version

        # set the layout of the translated object to match the english object
        trans_obj.setLayout(layout_en)

        # also set the layout of the default view
        if default_view_en:
            trans_obj[default_view_en].setLayout(layout_default_view_en)

        # get tile data
        if trans_obj.portal_type == 'collective.cover.content' and \
                one_step is True:
            # One step translation for covers/tiles
            json_data = get_object_fields_values(obj_en)

            tile_html_fields = []
            if 'tile' in json_data:
                for tile_id in json_data['tile'].keys():
                    tile_data = json_data['tile'][tile_id]
                    # LOOP tile text items
                    for key in tile_data['item'].keys():
                        # TODO add one step params
                        res = retrieve_translation_one_step(
                            'EN', tile_data['item'][key], [language.upper()],
                            uid=trans_obj.UID(),
                            obj_path=trans_obj_path, field=key,
                            tile_data=tile_data, tile_id=tile_id)
                        logger.info("One step translation tile: %s", res)
                    # LOOP tile HTML items
                    for key in tile_data['html'].keys():
                        value = tile_data['html'][key]
                        value = value.replace('\r\n', '')
                        try:
                            test_value = value + u"test"
                        except UnicodeDecodeError:
                            value = value.decode("utf-8")
                        tile_html_fields.append(
                            {'tile_id': tile_id, 'field': key, 'value': value}
                        )

            # TILE HTML fields translate in one call
            if len(tile_html_fields):
                if not trans_obj_path:
                    continue
                html_content = u"<!doctype html>" + \
                    u"<head><meta charset=utf-8></head><body>"
                for item in tile_html_fields:
                    html_tile = u"<div class='cca-translation-tile'" + \
                        u" data-field='" + item['field'] + u"'" + \
                        u" data-tile-id='" + item['tile_id'] + u"'" + \
                        u">" + item['value'] + u"</div>"
                    html_content += html_tile

                html_content += u"</body></html>"
                html_content = html_content.encode('utf-8')
                translated = retrieve_html_translation(
                    'EN',
                    html_content,
                    trans_obj_path,
                    language.upper(),
                    False,
                )
        elif trans_obj.portal_type == 'collective.cover.content':
            tiles_id = trans_obj.list_tiles()

            for tile_id in tiles_id:
                tile = trans_obj.get_tile(tile_id)
                for field in tile_fields:
                    value = tile.data.get(field)
                    if value:
                        translated = retrieve_translation(
                                'EN', value, [language.upper()])

                        if 'translated' in translated:
                            encoded_text = translated['transId'].encode(
                                    'latin-1')
                            tile.data.update({field: encoded_text})

                if isinstance(tile, RichTextWithTitle) or \
                   isinstance(tile, RichTextTile):
                    try:
                        value = tile.data.get('text').raw
                    except Exception:
                        value = None
                    if value:
                        html_content = u"<!doctype html>" + \
                            u"<head><meta charset=utf-8></head><body>"

                        value = value.replace('\r\n', '')
                        try:
                            test_value = value + u"test"
                        except UnicodeDecodeError:
                            value = value.decode("utf-8")
                        html_tile = u"<div class='cca-translation-tile'" + \
                            u" data-field='" + field + u"'" + \
                            u" data-tile-id='" + tile_id + u"'" + \
                            u">" + value + u"</div>"

                        html_content += html_tile

                        html_content += u"</body></html>"
                        html_content = html_content.encode('utf-8')
                        translated = retrieve_html_translation(
                            'EN',
                            html_content,
                            trans_obj_path,
                            language.upper(),
                            False,
                        )

                        if 'translated' in translated:
                            try:
                                encoded_text = translated['transId'].encode(
                                        'latin-1')
                                tile.data['text'].raw = encoded_text
                            except AttributeError:
                                logger.info("Error for tile. TODO improve.")
                                logger.info(tile_id)

        # send requests to translation service for each field
        # update field in obj
        rich_fields = []

        for key in fields:
            rich = False
            # print(key)
            if key in ['acronym', 'id', 'language', 'portal_type',
                       'contentType']:
                continue

            value = getattr(getattr(obj, key), 'raw', getattr(obj, key))

            # TODO clean code - this is already in step 4
            # if trans_obj.portal_type in ['Event', 'cca-event']:
            #     force_unlock(trans_obj)
            #     reindex = False
            #     if key == 'start':
            #         # setattr(trans_obj, key, obj.start)
            #         trans_obj.start = obj.start
            #         reindex = True
            #     if key == 'end':
            #         trans_obj.end = obj.end
            #         # setattr(trans_obj, key, obj.start)
            #         reindex = True
            #     if key == 'effective':
            #         trans_obj.setEffectiveDate(obj.effective_date)
            #         reindex = True
            #     if key == 'timezone':
            #         trans_obj.timezone = obj.timezone
            #         reindex = True
            #
            #     if reindex is True:
            #         # reindex object
            #         trans_obj._p_changed = True
            #         trans_obj.reindexObject()
            #         continue
            #
            #         # transaction.commit()

            if not value:
                continue

            if callable(value):
                # ignore datetimes
                if isinstance(value(), DateTime):
                    continue

                value = value()

            # ignore some value types
            if isinstance(value, bool) or \
               isinstance(value, int) or \
               isinstance(value, long) or \
               isinstance(value, tuple) or \
               isinstance(value, list) or \
               isinstance(value, set) or \
               isinstance(value, dict) or \
               isinstance(value, NamedBlobImage) or \
               isinstance(value, NamedBlobFile) or \
               isinstance(value, NamedImage) or \
               isinstance(value, NamedFile) or \
               isinstance(value, DateTime) or \
               isinstance(value, date) or \
               isinstance(value, RelationValue) or \
               isinstance(value, Geolocation):
                continue

            if isinstance(getattr(obj, key), RichTextValue):
                value = getattr(obj, key).raw.replace('\r\n', '')
                rich = True
                if key not in rich_fields:
                    rich_fields.append(key)

            if is_json(value):
                continue

            if key not in errors:
                errors.append(key)
            force_unlock(trans_obj)

            if one_step == True:
                translated = retrieve_translation_one_step(
                    'EN', value, [language.upper()], uid=trans_obj.UID(),
                    obj_path=trans_obj_path, field=key)
                continue

            translated = retrieve_translation('EN', value, [language.upper()])
            if 'translated' in translated:
                # TODO improve this part, after no more errors
                encoded_text = translated['transId'].encode('latin-1')

                source_richtext_types = [
                    'eea.climateadapt.publicationreport',
                    'eea.climateadapt.researchproject',
                    'eea.climateadapt.mapgraphdataset',
                    'eea.climateadapt.video',
                    ]

                if key == 'source' and \
                        obj.portal_type in source_richtext_types:
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
                    if isinstance(value, str) and key in ['funding_programme']:
                        setattr(trans_obj, key, translated['transId'])
                    else:
                        setattr(trans_obj, key, encoded_text)

                # reindex object
                trans_obj._p_changed = True
                trans_obj.reindexObject(idxs=[key])

        if len(rich_fields) > 0:
            html_content = u"<!doctype html><head><meta charset=utf-8></head>"
            html_content += u"<body>"

            for key in rich_fields:
                value = getattr(obj, key).raw.replace('\r\n', '')
                html_section = u"<div class='cca-translation-section'" + \
                    u" data-field='" + key + u"'>" + value + u"</div>"

                html_content += html_section

            html_content += u"</body></html>"
            html_content = html_content.encode('utf-8')
            res = retrieve_html_translation(
                'EN',
                html_content,
                trans_obj_path,
                language.upper(),
                False,
            )

    return {'errors': errors}


def initiate_translations(site, skip=0, version=None, language=None):
    skip = int(skip)
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    if version is None:
        return "Missing translation version. Status: /admin-translation-status"
    version = int(version)
    catalog = site.portal_catalog
    count = -1
    res = catalog.searchResults(path='/cca/en')
    errors = []
    debug_skip = False
    debug_skip_number = skip  # do not translate first objects

    if skip > 0:
        debug_skip = True
    total_objs = len(res)

    translate_only = False
    only = []  # Example: ['Event', 'cca-event']
    if len(only) > 0:
        translate_only = True  # translate only the specified content types

    for brain in res:
        count += 1

        if debug_skip is True and count < debug_skip_number:
            continue

        if translate_only is True and brain.portal_type not in only:
            continue

        logger.info("--------------------------------------------------------")
        logger.info(count)
        logger.info(total_objs)
        logger.info("--------------------------------------------------------")

        if brain.getPath() == '/cca/en' or brain.portal_type in ['LIF', 'LRF']:
            continue

        obj = brain.getObject()

        try:
            result = translate_obj(obj, language, version)
        except Exception as err:
            result = {'errors': [err]}
            logger.info(err)
            # errors.append(err)
            import pdb; pdb.set_trace()

        t_errors = result.get('errors', []) if result is not None else []
        if len(t_errors) > 0:
            for error in t_errors:
                if error not in errors:
                    errors.append(error)

        if count % 20 == 0:
            logger.info("Processed %s objects" % count)
            transaction.commit()

    logger.info("DONE")
    logger.info(errors)
    transaction.commit()

def translations_status(site, language=None):
    if language is None:
        return "Missing language."

    path = '/cca/' + language
    catalog = site.portal_catalog
    brains = catalog.searchResults(path=path)

    versions = defaultdict(int)
    template = "<p>{} at version {}</p>"
    logger.info("Translations status:")

    for brain in brains:
        obj = brain.getObject()
        obj_version = int(getattr(obj, 'version', 0))
        versions[obj_version] += 1

    res = []
    for k, v in versions.items():
        res.append(template.format(v, k))

    logger.info(res)
    return "".join(res)


def verify_cloned_language(site, language=None):
    """ Get all objects in english and check if all of them are cloned for
        given language. Also make sure all paths are similar.
        Correct:
            /cca/en/obj-path
            /cca/ro/obj-path
        Wrong:
            /cca/en/obj-path
            /cca/ro/obj-path-ro-ro-ro
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    brains = catalog.searchResults(path='/cca/en')
    site_url = portal.getSite().absolute_url()
    logger.info("I will list the missing objects if any. Checking...")

    res = []
    found = 0  # translation found with correct path
    found_changed = 0  # translation found but with different path
    not_found = 0  # translation not found
    for brain in brains:
        obj = brain.getObject()
        obj_url = obj.absolute_url()
        obj_path = '/cca' + obj_url.split(site_url)[-1]
        prefix = '/cca/' + language.lower() + '/'
        trans_obj_path = obj_path.replace('/cca/en/', prefix)
        try:
            trans_obj = site.unrestrictedTraverse(trans_obj_path)
            found += 1
        except Exception:
            res.append(trans_obj_path)
            translations = TranslationManager(obj).get_translations()
            if language in translations:
                trans_obj = translations[language]
                new_url = trans_obj.absolute_url()
                res.append("Found as: " + new_url)
                found_changed += 1
                logger.info(trans_obj_path)
                logger.info("Found as %s", new_url)
            else:
                not_found += 1
                res.append("Not found.")
                logger.info("Not found: %s", trans_obj_path)

    logger.info("Found: %s. Found with different path: %s. Not found: %s.",
                found, found_changed, not_found)

    return "\n".join(res)

def verify_translation_fields(site, request):
    language = request.get('language', None)
    uid = request.get('uid', None)
    stop_pdb = request.get('stop_pdb', None)
    portal_type = request.get('portal_type', None)
    """ Get all objects in english and check if all of them are cloned for
        given language and with fields filled.
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    #brains = catalog.searchResults(path='/cca/en')
    catalogSearch = {}
    catalogSearch['path'] = '/cca/en'
    if uid:
        catalogSearch['UID'] = uid
    brains = catalog.searchResults(catalogSearch)
    site_url = portal.getSite().absolute_url()
    logger.info("I will list the missing translation fields. Checking...")

    res = []
    total_items = 0  # total translatable eng objects
    found = 0  # found end objects
    found_missing = 0  # missing at least one attribute
    not_found = 0  # eng obj not found
    missing_values = 0  # count the missing field values

    report = {}
    report_detalied = []
    skip_items = ['.jpg','.pdf','.png']
    skip_fields = ["sync_uid", "allow_discussion"]
    # skip_types = ['File', 'Image']

    for brain in brains:
        obj = brain.getObject()
        if portal_type and portal_type!=obj.portal_type:
            continue
        if is_obj_skipped_for_translation(obj):
            continue

        obj_url = obj.absolute_url()

        # if obj.portal_type in skip_types:
        #     continue

        if obj.portal_type not in report:
            report[obj.portal_type] = {}

        #if '.jpg' in obj_url:
        if any(skip_item in obj_url for skip_item in skip_items):
            continue
        total_items += 1
        obj_path = '/cca' + obj_url.split(site_url)[-1]
        # logger.info("Will check: %s", obj_path)
        translations = TranslationManager(obj).get_translations()
        if language not in translations:
            #add message regarding no translation found
            logger.info("Not found: %s", obj_path)
            not_found += 1
            continue
        trans_obj = translations[language]

        # get behavior fields and values
        behavior_assignable = IBehaviorAssignable(obj)
        fields = {}
        if behavior_assignable:
            behaviors = behavior_assignable.enumerateBehaviors()
            for behavior in behaviors:
                for k, v in getFieldsInOrder(behavior.interface):
                    fields.update({k: v})
        for k, v in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
            fields.update({k: v})

        logger.info("%s URL: %s", found, trans_obj.absolute_url())
        fields_missing = []
        if stop_pdb:
            import pdb; pdb.set_trace()
        for field in fields.keys():
            if field in skip_fields:
                continue
            #TODO: check if we need to log if this is FALSE
            if not hasattr(obj, field):
                continue
            if not hasattr(trans_obj, field):
                fields_missing.append(field)
                continue
            #if bool(getattr(obj, field)) and not bool(getattr(trans_obj,field)):
            #        fields_missing.append(field)
            mark_field = False
            if isinstance(getattr(obj, field), RichTextValue):
                obj_val = getattr(obj, field).output
                trans_obj_val = ''
                if isinstance(getattr(trans_obj, field), RichTextValue):
                    trans_obj_val = getattr(trans_obj, field).output
                else:
                    trans_obj_val = getattr(trans_obj, field, None)
                    if not trans_obj_val:
                        trans_obj_val = ''
                if len(obj_val) and 0 == len(trans_obj_val):
                    mark_field = True
            elif isinstance(getattr(obj, field), unicode):
                obj_val = getattr(obj, field)
                trans_obj_val = ''
                if isinstance(getattr(trans_obj, field), unicode):
                    trans_obj_val = getattr(trans_obj, field)
                elif isinstance(getattr(trans_obj, field), RichTextValue):
                    trans_obj_val = getattr(trans_obj, field).output
                else:
                    trans_obj_val = getattr(trans_obj, field, '')
                    if not trans_obj_val:
                        trans_obj_val = ''
                if len(obj_val) and 0 == len(trans_obj_val):
                    mark_field = True
            else:
                missing = object()
                if not mark_field and not getattr(obj,field,missing) in (missing, None) and getattr(trans_obj,field,missing) in (missing, None):
                    mark_field = True
            if mark_field:
                fields_missing.append(field)
                missing_values += 1

                if field not in report[obj.portal_type]:
                    report[obj.portal_type][field] = 0

                prev_value = report[obj.portal_type][field]
                report[obj.portal_type][field] = prev_value + 1

        if len(fields_missing):
            logger.info("FIELDS NOT SET: %s %s", trans_obj.absolute_url(), fields_missing)
            report_detalied.append({
                    'url': trans_obj.absolute_url(),
                    'brain_uid': brain.UID,
                    'missing': fields_missing,
                    'portal_type': trans_obj.portal_type
                })
            found_missing += 1

        #import pdb; pdb.set_trace()
        found += 1

    logger.info("TotalItems: %s, Found with correct data: %s. Found with mising data: %s. Not found: %s. Missing values: %s",
                total_items, found, found_missing, not_found, missing_values)

    report['_details'] = report_detalied
    report['_stats'] = {'file':total_items,'found':found,'found_missing':found_missing,'not_found':not_found,'missing_value':missing_values}
    json_object = json.dumps(report, indent=4)
    with open("/tmp/translation_report.json", "w") as outfile:
        outfile.write(json_object)

    return "\n".join(res)

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

def get_object_fields_values(obj):
    #TODO: perhaps a list by each portal_type
    skip_fields = ['c3s_identifier', 'contact_email', 'contact_name', 'details_app_toolbox_url', 'duration', 'event_url', 'funding_programme', 'method', 'other_contributor',
        'organisational_contact_information', 'organisational_websites', 'overview_app_toolbox_url', 'partners_source_link', 'remoteUrl', 'storage_type', 'sync_uid','timezone',
        'template_layout']
    tile_fields = ['title', 'text', 'description', 'tile_title', 'footer', 'alt_text']

    data = {}
    data['portal_type'] = obj.portal_type
    data['path'] = obj.absolute_url()
    data['item'] = {}
    data['html'] = {}
    data['tile'] = {}
    # get tile data
    #import pdb; pdb.set_trace()
    if obj.portal_type == 'collective.cover.content':
        tiles_id = obj.list_tiles()
        for tile_id in tiles_id:
            data['tile'][tile_id] = {'item':{},'html':{}}
            tile = obj.get_tile(tile_id)
            for field in tile_fields:
                value = None
                if isinstance(tile, RichTextWithTitle) or \
                   isinstance(tile, RichTextTile):
                    if field in tile_fields:
                        try:
                            if isinstance(tile.data.get(field), RichTextValue):
                                value = tile.data.get(field).raw
                                if value:
                                    data['tile'][tile_id]['html'][field] = value
                            else:
                                value = tile.data.get(field)
                                if value:
                                    data['tile'][tile_id]['item'][field] = value
                        except Exception:
                            value = None
                else:
                    value = tile.data.get(field, None)
                    if value:
                        data['tile'][tile_id]['item'][field] = value
    fields = get_object_fields(obj)
    for key in fields:
        rich = False
        # print(key)
        if key in ['acronym', 'id', 'language', 'portal_type',
                   'contentType']:
            continue
        if key in skip_fields:
            continue

        value = getattr(getattr(obj, key), 'raw', getattr(obj, key))

        if not value:
            continue

        if callable(value):
            # ignore datetimes
            if isinstance(value(), DateTime):
                continue

            value = value()

        # ignore some value types
        if isinstance(value, bool) or \
           isinstance(value, int) or \
           isinstance(value, long) or \
           isinstance(value, tuple) or \
           isinstance(value, list) or \
           isinstance(value, set) or \
           isinstance(value, dict) or \
           isinstance(value, NamedBlobImage) or \
           isinstance(value, NamedBlobFile) or \
           isinstance(value, NamedImage) or \
           isinstance(value, NamedFile) or \
           isinstance(value, DateTime) or \
           isinstance(value, date) or \
           isinstance(value, RelationValue) or \
           isinstance(value, Geolocation):
            continue

        if isinstance(getattr(obj, key), RichTextValue):
            value = getattr(obj, key).raw.replace('\r\n', '')
            data['html'][key] = value
            continue

        if is_json(value):
            continue

        data['item'][key] = value
    return data

def is_obj_skipped_for_translation(obj):
    #skip by portal types
    if obj.portal_type in ['eea.climateadapt.city_profile','LIF']:
        return True

    #skip by string in path
    skip_path_items = ['.jpg','.pdf','.png']
    obj_url = obj.absolute_url()
    if any(skip_item in obj_url for skip_item in skip_path_items):
        return True

    #TODO: add here archived and other rules
    return False

def get_translation_object(obj, language):
    try:
        translations = TranslationManager(obj).get_translations()
    except Exception:
        return None

    if language not in translations:
        return None
    trans_obj = translations[language]
    return trans_obj

def get_translation_object_path(obj, language, site_url):
    trans_obj = get_translation_object(obj, language)
    if not trans_obj:
        return None
    trans_obj_url = trans_obj.absolute_url()
    return '/cca' + trans_obj_url.split(site_url)[-1]

def get_translation_object_from_uid(json_uid_file, catalog):
    brains = catalog.searchResults(UID=json_uid_file.replace(".json",""))
    if 0 == len(brains):
        return None
    return brains[0].getObject()

def get_translation_json_files(uid=None):
    json_files = []
    if uid:
        if os.path.exists("/tmp/jsons/"+str(uid)+".json"):
            json_files.append(str(uid)+".json")
    else:
        json_files = os.listdir("/tmp/jsons/")
    return json_files

def get_trans_obj_path_for_obj(obj):
    res = {}
    try:
        translations = TranslationManager(obj).get_translations()
    except:
        logger.info("Error at getting translations for %s", obj.absolute_url())
        translations = []

    for language in translations:
        trans_obj = translations[language]
        trans_obj_url = trans_obj.absolute_url()

        res[language] = trans_obj_url

    return {"translated_obj_paths": res}

def translation_step_1(site, request):
    """ Save all items for translation in a json file
    """
    limit = int(request.get('limit', 0))
    search_path = request.get('search_path', None)
    portal_type = request.get('portal_type', None)

    catalog = site.portal_catalog
    search_data = {}
    search_data['path'] = '/cca/en'
    if limit:
        search_data['sort_limit'] = limit
    if portal_type:
        search_data['portal_type'] = portal_type
    #if search_path:
    #    search_data['path'] = search_path

    brains = catalog.searchResults(search_data)
    site_url = portal.getSite().absolute_url()
    logger.info("I will start to create json files. Checking...")

    res = {}
    total_items = 0  # total translatable eng objects

    for brain in brains:
        obj = brain.getObject()
        obj_url = obj.absolute_url()
        if is_obj_skipped_for_translation(obj):
            continue
        if search_path:
            if search_path not in obj_url:
                continue
        logger.info("PROCESS: %s", obj_url)

        data = get_object_fields_values(obj)

        # add the trans_obj_path for each language into the json
        translation_paths = get_trans_obj_path_for_obj(obj)
        data.update(translation_paths)

        json_object = json.dumps(data, indent = 4)

        with open("/tmp/jsons/"+brain.UID+".json", "w") as outfile:
            outfile.write(json_object)
        if obj.portal_type not in res:
            res[obj.portal_type] = 1
        else:
            res[obj.portal_type] += 1

    logger.info("RESP %s", res)

def translation_step_2(site, request, force_uid=None):
    language = request.get('language', None)
    uid = request.get('uid', None)
    limit = int(request.get('limit', 0))
    offset = int(request.get('offset', 0))
    portal_type = request.get('portal_type', None)
    if force_uid:
        uid = force_uid

    """ Get all jsons objects in english and call etranslation for each field
        to be translated in specified language.
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    site_url = portal.getSite().absolute_url()
    #import pdb; pdb.set_trace()
    json_files = get_translation_json_files(uid)

    report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report = {}
    report['date'] = {'start':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'end':None}
    report['filter'] = {'language':language, 'uid':uid, 'limit': limit, 'offset': offset, 'portal_type': portal_type}
    total_files = len(json_files)  # total translatable eng objects (not unique)
    nr_files = 0  # total translatable eng objects (not unique)
    nr_items = 0  # total translatable eng objects (not unique)
    nr_html_items = 0  # total translatable eng objects (not unique)
    nr_items_translated = 0  # found translated objects
    #import pdb; pdb.set_trace()
    if limit:
        json_files.sort()
        json_files = json_files[offset: offset+limit]

    for json_file in json_files:
        file = open("/tmp/jsons/"+json_file, "r")
        json_content = file.read()
        json_data = json.loads(json_content)
        if portal_type and portal_type!=json_data['portal_type']:
            continue
        nr_files += 1
        #LOPP object tiles
        tile_html_fields = []
        if 'tile' in json_data:
            for tile_id in json_data['tile'].keys():
                tile_data = json_data['tile'][tile_id]
                #LOOP tile text items
                for key in tile_data['item'].keys():
                    res = retrieve_translation('EN', tile_data['item'][key], [language.upper()])
                    nr_items += 1
                    if 'translated' in res:
                        nr_items_translated += 1
                #LOOP tile HTML items
                for key in tile_data['html'].keys():
                    value = tile_data['html'][key]
                    value = value.replace('\r\n', '')
                    try:
                        test_value = value + u"test"
                    except UnicodeDecodeError:
                        value = value.decode("utf-8")
                    tile_html_fields.append({'tile_id':tile_id,'field':key, 'value':value})
        #TILE HTML fields translate in one call
        if len(tile_html_fields):
            nr_html_items += 1
            obj = get_translation_object_from_uid(json_file, catalog)
            trans_obj_path = get_translation_object_path(obj, language, site_url)
            if not trans_obj_path:
                continue
            html_content = u"<!doctype html>" + \
                u"<head><meta charset=utf-8></head><body>"
            for item in tile_html_fields:
                html_tile = u"<div class='cca-translation-tile'" + \
                    u" data-field='" + item['field'] + u"'" + \
                    u" data-tile-id='" + item['tile_id'] + u"'" + \
                    u">" + item['value'] + u"</div>"
                html_content += html_tile

            html_content += u"</body></html>"
            html_content = html_content.encode('utf-8')
            translated = retrieve_html_translation(
                'EN',
                html_content,
                trans_obj_path,
                language.upper(),
                False,
            )

        #LOOP object text items
        for key in json_data['item'].keys():
            res = retrieve_translation('EN', json_data['item'][key], [language.upper()])
            nr_items += 1
            if 'translated' in res:
                nr_items_translated += 1
        #LOOP object HTML items
        if len(json_data['html']):
            nr_html_items += 1
            obj = get_translation_object_from_uid(json_file, catalog)
            trans_obj_path = get_translation_object_path(obj, language, site_url)
            if not trans_obj_path:
                continue

            html_content = u"<!doctype html><head><meta charset=utf-8></head>"
            html_content += u"<body>"

            for key in json_data['html'].keys():
                value = json_data['html'][key].replace('\r\n', '')
                html_section = u"<div class='cca-translation-section'" + \
                    u" data-field='" + key + u"'>" + value + u"</div>"

                html_content += html_section

            html_content += u"</body></html>"
            html_content = html_content.encode('utf-8')
            res = retrieve_html_translation(
                'EN',
                html_content,
                trans_obj_path,
                language.upper(),
                False,
            )
        logger.info("TransStep2 File  %s from %s, total files %s",nr_files, len(json_files), total_files)
        if not force_uid:
            report['date']['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report['response'] = {'items': {'nr_files': nr_files, 'nr':nr_items, 'nr_already_translated':nr_items_translated},'htmls':nr_html_items, 'portal_type':portal_type}
            report['total_files'] = total_files
            report['status'] = 'Processing'

            json_object = json.dumps(report, indent = 4)
            with open("/tmp/translate_step_2_"+language+"_"+report_date+".json", "w") as outfile:
                outfile.write(json_object)
        time.sleep(0.5)

    if not force_uid:
        report['date']['end'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report['status'] = 'Done'
        report['response'] = {'items': {'nr_files': nr_files, 'nr':nr_items, 'nr_already_translated':nr_items_translated},'htmls':nr_html_items}
        report['total_files'] = total_files

        json_object = json.dumps(report, indent = 4)
        with open("/tmp/translate_step_2_"+language+"_"+report_date+".json", "w") as outfile:
            outfile.write(json_object)

    logger.info("Files: %s, TotalItems: %s, Already translated: %s HtmlItems: %s",
                nr_files, nr_items, nr_items_translated, nr_html_items)

def translation_step_3_one_file(json_file, language, catalog, portal_type = None):
    obj = get_translation_object_from_uid(json_file, catalog)
    trans_obj = get_translation_object(obj, language)
    if trans_obj is None:
        return

    file = open("/tmp/jsons/"+json_file, "r")
    json_content = file.read()
    json_data = json.loads(json_content)
    if portal_type and portal_type!=json_data['portal_type']:
        return
    have_change = False
    if 'tile' in json_data:
        for tile_id in json_data['tile'].keys():
            tile_data = json_data['tile'][tile_id]
            tile_annot_id = 'plone.tiles.data.' + tile_id
            tile = trans_obj.__annotations__.get(tile_annot_id, None)
            if not tile:
                continue
            for key in tile_data['item'].keys():
                try:
                    update = tile.data
                except AttributeError:
                    update = tile
                translated_msg = get_translated(tile_data['item'][key], language.upper())
                if translated_msg:
                    try:
                        update[key] = translated_msg.encode('latin-1')
                    except Exception:
                        update[key] = translated_msg
                    have_change = True
                # tile.data.update(update)
                trans_obj.__annotations__[tile_annot_id] = update

    for key in json_data['item'].keys():
        translated_msg = get_translated(json_data['item'][key], language.upper())
        if translated_msg:
            encoded_text = translated_msg.encode('latin-1')

            source_richtext_types = [
                'eea.climateadapt.publicationreport',
                'eea.climateadapt.researchproject',
                'eea.climateadapt.mapgraphdataset',
                'eea.climateadapt.video',
                ]

            if key == 'source' and \
                    obj.portal_type in source_richtext_types:
                setattr(trans_obj, key, getattr(obj, key))
                # solves Can not convert 'Elsevier' to an IRichTextValue
                setattr(trans_obj, key, RichTextValue(encoded_text))
                have_change = True
            else:
                try:
                    setattr(trans_obj, key, encoded_text)
                    have_change = True
                except AttributeError:
                    logger.info("AttributeError for obj: %s key: %s",
                                obj.absolute_url(), key)
    if have_change:
        trans_obj._p_changed = True
        trans_obj.reindexObject()

def translation_step_3(site, request):
    """ Get all jsons objects in english and overwrite targeted language
        object with translations.
    """
    language = request.get('language', None)
    uid = request.get('uid', None)
    limit = int(request.get('limit', 0))
    offset = int(request.get('offset', 0))
    portal_type = request.get('portal_type', None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    json_files = get_translation_json_files(uid)
    total_files = len(json_files)  # total translatable eng objects (not unique)

    report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report = {}
    report['date'] = {'start':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'end':None}
    report['filter'] = {'language':language, 'uid':uid, 'limit': limit, 'offset': offset, 'portal_type': portal_type}
    report['total_files'] = total_files

    if limit:
        json_files.sort()
        json_files = json_files[offset: offset+limit]

    nr_files = 0  # total translatable eng objects (not unique)
    nr_items = 0  # total translatable eng objects (not unique)
    nr_items_translated = 0  # found translated objects

    for json_file in json_files:
        nr_files += 1
        logger.info("PROCESSING file: %s", nr_files)

        try:
            translation_step_3_one_file(
                    json_file, language, catalog, portal_type)
            transaction.commit()  # make sure tiles are saved (encoding issue)
        except Exception as err:
            logger.info("ERROR")  # TODO improve this
            logger.info(err)

        report['date']['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report['response'] = {'last_item': json_file, 'files_processd': nr_files}
        report['status'] = 'Processing'

        json_object = json.dumps(report, indent = 4)
        with open("/tmp/translate_step_3_"+language+"_"+report_date+".json", "w") as outfile:
            outfile.write(json_object)

    report['date']['end'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report['status'] = 'Done'

    json_object = json.dumps(report, indent = 4)
    with open("/tmp/translate_step_3_"+language+"_"+report_date+".json", "w") as outfile:
        outfile.write(json_object)

    logger.info("Finalize step 3")


def translation_step_4(site, request):
    """ Copy fields values from en to given language for language independent
        fields.
    """
    language = request.get('language', None)
    uid = request.get('uid', None)
    limit = int(request.get('limit', 0))
    offset = int(request.get('offset', 0))
    portal_type = request.get('portal_type', None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"

    catalog = site.portal_catalog
    search_data = {}
    search_data['path'] = '/cca/en'
    if uid:
        search_data['UID'] = uid
    if limit:
        search_data['sort_limit'] = limit
    if portal_type:
        search_data['portal_type'] = portal_type
    #import pdb; pdb.set_trace()

    #brains = catalog.searchResults(path='/cca/en', sort_limit=limit)
    brains = catalog.searchResults(search_data)

    #brains = catalog.searchResults(path='/cca/en')
    site_url = portal.getSite().absolute_url()
    logger.info("Start copying values for language independent fields...")

    language_independent_fields = {
        "Folder": ["effective"],
        "eea.climateadapt.video": ["effective"],
        "Link": ["effective"],
        "eea.climateadapt.c3sindicator": ["effective"],
        "eea.climateadapt.city_profile": ["effective"],
        "eea.climateadapt.researchproject": ["effective"],
        "eea.climateadapt.tool": [
            "spatial_values", "storage_type", "publication_date", "effective",
            ],
        "eea.climateadapt.guidancedocument": [
            "storage_type", "spatial_values", "effective",
            ],
        "EasyForm": ["showFields", "effective"],
        "eea.climateadapt.adaptationoption": [
            "implementation_type", "effective",
            ],
        "eea.climateadapt.mapgraphdataset": [
            "storage_type", "spatial_values", "effective",
            ],
        "Collection": ["sort_reversed", "query", "effective"],
        "Document": ["table_of_contents", "effective"],
        "News Item": ["health_impacts", "image", "effective"],
        "eea.climateadapt.casestudy": [
            "geolocation", "implementation_type", "spatial_values",
            "effective",
            ],
        "eea.climateadapt.aceproject": [
            "specialtagging", "spatial_values", "funding_programme",
            "effective"
            ],
        "eea.climateadapt.indicator": [
            "publication_date", "storage_type", "spatial_values", "effective",
            ],
        "eea.climateadapt.informationportal": [
            "spatial_values", "storage_type", "publication_date", "effective"
            ],
        "eea.climateadapt.organisation": [
            "storage_type", "spatial_values", "publication_date", "effective",
            ],
        "eea.climateadapt.publicationreport": [
            "storage_type", "spatial_values", "metadata", "effective",
            ],
        "Event": [
            "start", "end", "effective", "timezone", "event_url",
            "health_impacts", "contact_email", "location", "contact_name",
            "effective",
            ],
        "cca-event": [
            "start", "end", "effective", "timezone", "contact_email",
            "contact_name"
            ],
        "File": ["file", "effective"],
        "Image": ["image", "effective"],
        "collective.cover.content": ["title", "effective",'template_layout'],
    }

    obj_count = 0
    for brain in brains:
        if uid and uid != brain.UID:
            continue
        obj = brain.getObject()
        obj_count += 1
        logger.info("PROCESSING obj: %s", obj_count)

        try:
            translations = TranslationManager(obj).get_translations()
        except:
            pass

        try:
            trans_obj = translations[language]
        except KeyError:
            logger.info("Missing translation for: %s", obj.absolute_url())
            continue

        reindex = False

        #import pdb; pdb.set_trace()
        if obj.portal_type == 'collective.cover.content':
            #Set propper collection for current language
            #WE supose to have only one cards_tile in the list of tiles
            try:
                data_tiles = obj.get_tiles()
                for data_tile in data_tiles:
                    if data_tile['type'] == 'eea.climateadapt.cards_tile':
                        data_trans_tiles = obj.get_tiles()
                        for data_trans_tile in data_trans_tiles:
                            if data_trans_tile['type'] == 'eea.climateadapt.cards_tile':
                                #import pdb; pdb.set_trace()
                                tile = obj.get_tile(data_tile['id'])
                                try:
                                    trans_tile = trans_obj.get_tile(data_trans_tile['id'])
                                except ValueError:
                                    logger.info("Tile not found.")
                                    trans_tile = None

                                if trans_tile is not None:
                                    collection_obj = uuidToObject(tile.data["uuid"])
                                    collection_trans_obj = get_translation_object(collection_obj, language)

                                    dataManager = ITileDataManager(trans_tile)

                                    temp = dataManager.get()
                                    try:
                                        temp['uuid'] = IUUID(collection_trans_obj)
                                    except TypeError:
                                        logger.info("Collection not found.")

                                    dataManager.set(temp)
            except KeyError:
                logger.info("Problem setting collection in tile for language")

            force_unlock(obj)
            layout_en = obj.getLayout()
            if layout_en:
                reindex = True
                trans_obj.setLayout(layout_en)

        if obj.portal_type == 'Folder':
            force_unlock(obj)

            layout_en = obj.getLayout()
            default_view_en = obj.getDefaultPage()
            layout_default_view_en = None
            if default_view_en:
                try:
                    trans_obj.setDefaultPage(default_view_en)
                    reindex = True
                except:
                    logger.info("Can't set default page for: %s",
                                trans_obj.absolute_url())
            #else:
            if not reindex:
                reindex = True
                trans_obj.setLayout(layout_en)

            if default_view_en is not None:
                layout_default_view_en = obj[default_view_en].getLayout()

            # set the layout of the translated object to match the EN object

            # also set the layout of the default view
            if layout_default_view_en:
                try:
                    trans_obj[default_view_en].setLayout(layout_default_view_en)
                except:
                    logger.info("Can't set layout for: %s",
                                trans_obj.absolute_url())
                    continue

            trans_obj._p_changed = True
            trans_obj.reindexObject()

        if obj.portal_type in language_independent_fields:
            force_unlock(obj)
            obj_url = obj.absolute_url()
            logger.info("PROCESS: %s", obj_url)

            try:
                translations = TranslationManager(obj).get_translations()
            except:
                pass

            try:
                trans_obj = translations[language]
            except KeyError:
                logger.info("Missing translation for: %s", obj_url)
                continue

            #force_unlock(trans_obj)
            #reindex = False

            fields = language_independent_fields[obj.portal_type]
            for key in fields:
                logger.info("Field: %s", key)

                # TODO simplify this
                if key == 'start':
                    # setattr(trans_obj, key, obj.start)
                    trans_obj.start = obj.start
                    reindex = True
                elif key == 'end':
                    trans_obj.end = obj.end
                    # setattr(trans_obj, key, obj.start)
                    reindex = True
                elif key == 'effective':
                    trans_obj.setEffectiveDate(obj.effective_date)
                    reindex = True
                elif key == 'timezone':
                    trans_obj.timezone = obj.timezone
                    reindex = True
                else:
                    try:
                        setattr(trans_obj, key, getattr(obj, key))
                        reindex = True
                    except Exception:
                        logger.info("Skip: %s %s", obj.portal_type, key)

        if reindex is True:
            # reindex object
            trans_obj._p_changed = True
            trans_obj.reindexObject()
            continue

    logger.info("Finalize step 4")
    return("Finalize step 4")


def translation_repaire(site, request):
    """ Get all jsons objects in english and overwrite targeted language
        object with translations.
    """
    language = request.get('language', None)
    file = request.get('file', None)
    uid = request.get('uid', None)
    limit = int(request.get('limit', 0))
    offset = int(request.get('offset', 0))
    portal_type = request.get('portal_type', None)
    stop_pdb = request.get('stop_pdb', None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    if file is None:
        return "Missing file parameter. (Example: ?file=ABC will process /tmp/ABC.json)"
    file = open("/tmp/"+file+".json", "r")
    json_content = file.read()
    if not is_json(json_content):
        return "Looks like we the file is not valid json"
    json_data = json.loads(json_content)

    #import pdb; pdb.set_trace()
    if '_details' not in json_data:
        return "Details key was not found in json"

    items = json_data['_details']
    if stop_pdb:
        import pdb; pdb.set_trace()
    for item in items:
        translation_step_2(site, request, item['brain_uid'])


def translation_repaire_step_3(site, request):
    """ Get all jsons objects in english and overwrite targeted language
        object with translations.
    """
    language = request.get('language', None)
    file = request.get('file', None)
    uid = request.get('uid', None)
    limit = int(request.get('limit', 0))
    offset = int(request.get('offset', 0))
    portal_type = request.get('portal_type', None)
    stop_pdb = request.get('stop_pdb', None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    if file is None:
        return "Missing file parameter. (Example: ?file=ABC will process /tmp/ABC.json)"
    file = open("/tmp/"+file+".json", "r")
    json_content = file.read()
    if not is_json(json_content):
        return "Looks like we the file is not valid json"
    json_data = json.loads(json_content)

    #import pdb; pdb.set_trace()
    if '_details' not in json_data:
        return "Details key was not found in json"

    items = json_data['_details']
    if stop_pdb:
        import pdb; pdb.set_trace()
    catalog = site.portal_catalog
    for item in items:
        if uid and uid != brain.UID:
            continue
        if portal_type and portal_type!=item['portal_type']:
            continue
        if stop_pdb:
            import pdb; pdb.set_trace()
        translation_step_3_one_file(item['brain_uid']+'.json', language, catalog, portal_type)


def translation_list_type_fields(site):
    """ Show each field for each type
    """
    catalog = site.portal_catalog
    #TODO: remove this, it is jsut for demo purpose
    limit=10000
    brains = catalog.searchResults(path='/cca/en', sort_limit=limit)
    site_url = portal.getSite().absolute_url()
    logger.info("I will start to create json files. Checking...")

    res = {}
    total_items = 0  # total translatable eng objects

    for brain in brains:
        obj = brain.getObject()
        obj_url = obj.absolute_url()
        logger.info("PROCESS: %s", obj_url)
        if is_obj_skipped_for_translation(obj):
            continue
        data = get_object_fields_values(obj)

        if obj.portal_type == 'collective.cover.content':
            if obj.portal_type not in res:
                res[obj.portal_type] = {}
            #import pdb; pdb.set_trace()
            tiles_id = obj.list_tiles()
            for tile_id in tiles_id:
                tile = obj.get_tile(tile_id)
                tile_name = tile.__class__.__name__
                if tile_name not in res[obj.portal_type]:
                    res[obj.portal_type][tile_name] = {}
                for field in tile.data.keys():
                    if field not in res[obj.portal_type][tile_name]:
                        res[obj.portal_type][tile_name][field] = []
                    if len(res[obj.portal_type][tile_name][field])<5:
                        res[obj.portal_type][tile_name][field].append(obj_url)
        else:
            if obj.portal_type not in res:
                res[obj.portal_type] = {"item":[],"html":[]}
            for key in data['item']:
                if key not in res[obj.portal_type]["item"]:
                    res[obj.portal_type]["item"].append(key)
            for key in data['html']:
                if key not in res[obj.portal_type]["html"]:
                    res[obj.portal_type]["html"].append(key)

    json_object = json.dumps(res, indent = 4)
    #import pdb; pdb.set_trace()

    with open("/tmp/portal_type_fields.json", "w") as outfile:
        outfile.write(json_object)

def translations_status_by_version(site, version=0, language=None):
    """ Show the list of urls of a version and language
    """
    if language is None:
        return "Missing language."

    path = '/cca/' + language
    version = int(version)
    catalog = site.portal_catalog
    brains = catalog.searchResults()
    brains = catalog.searchResults(path=path)

    res = []
    template = "<p>{}</p>"

    for brain in brains:
        obj = brain.getObject()
        obj_version = int(getattr(obj, 'version', 0))

        if obj_version != version:
            continue

        res.append(template.format(obj.absolute_url()))

    return "".join(res)


def get_tile_type(tile, from_cover, to_cover):
    """ Return tile type
    """
    tiles_types = {
        'RichTextWithTitle': 'eea.climateadapt.richtext_with_title',
        'EmbedTile': 'collective.cover.embed',
        'RichTextTile': 'collective.cover.richtext',
        'SearchAceContentTile': 'eea.climateadapt.search_acecontent',
        'GenericViewTile': 'eea.climateadapt.genericview',
        'RelevantAceContentItemsTile': 'eea.climateadapt.relevant_acecontent',
        'ASTNavigationTile': 'eea.climateadapt.ast_navigation',
        'ASTHeaderTile': 'eea.climateadapt.ast_header',
        'FilterAceContentItemsTile': 'eea.climateadapt.filter_acecontent',
        'TransRegionalSelectTile': 'eea.climateadapt.transregionselect',
        'SectionNavTile': 'eea.climateadapt.section_nav',
        'CountrySelectTile': 'eea.climateadapt.countryselect',
        'BannerTile': 'collective.cover.banner',
        'ShareInfoTile': 'eea.climateadapt.shareinfo',
        'FormTile': 'eea.climateadapt.formtile',
        'UrbanMenuTile': 'eea.climateadapt.urbanmenu',
        'CardsTile': 'eea.climateadapt.cards_tile',
    }
    for a_type in tiles_types.keys():
        if a_type in str(type(tile)):
            return tiles_types[a_type]

    return None


def copy_tiles(tiles, from_cover, to_cover):
    """ Copy the tiles from cover to translated cover
    """
    logger.info("Copy tiles")
    logger.info(from_cover.absolute_url())
    logger.info(to_cover.absolute_url())
    for tile in tiles:
        tile_type = get_tile_type(tile, from_cover, to_cover)

        if tile_type is not None:
            from_tile = from_cover.restrictedTraverse(
                '@@{0}/{1}'.format(tile_type, tile.id)
            )

            to_tile = to_cover.restrictedTraverse(
                '@@{0}/{1}'.format(tile_type, tile.id)
            )

            from_data_mgr = ITileDataManager(from_tile)
            to_data_mgr = ITileDataManager(to_tile)
            to_data_mgr.set(from_data_mgr.get())

        else:
            logger.info("Missing tile type")
            import pdb; pdb.set_trace()


def check_full_path_exists(obj, language):
    """ Create full path for a object
    """

    parent = obj.getParentNode()
    path = parent.getPhysicalPath()
    if len(path)<=2:
        return True

    translations = TranslationManager(parent).get_translations()
    if language not in translations:
        ##TODO, what if the parent path already exist in language
        ## but is not linked in translation manager
        create_translation_object(parent, language)

def create_translation_object(obj, language):
    """ Create translation object for an obj
    """
    if language in TranslationManager(obj).get_translations():
        logger.info("Skip creating translation. Already exists.")
        return

    check_full_path_exists(obj, language)
    factory = DefaultTranslationFactory(obj)

    translated_object = factory(language)

    TranslationManager(obj).register_translation(language, translated_object)

    # https://github.com/plone/plone.app.multilingual/blob/2.x/src/plone/app/multilingual/manager.py#L85
    # translated_object.reindexObject()   ^ already reindexed.

    if obj.portal_type == 'collective.cover.content':
        tiles = [obj.get_tile(x) for x in obj.list_tiles()]
        translated_object.cover_layout = obj.cover_layout
        copy_tiles(tiles, obj, translated_object)

    translated_object.reindexObject()


def get_all_objs(container):
    """ Get the container's objects
    """
    all_objs = []

    def get_objs(context):
        contents = api.content.find(context=context, depth=1)
        for item in contents:
            all_objs.append(item)

        for item in contents:
            get_objs(item.getObject())

    get_objs(container)

    return all_objs


def execute_trans_script(site, language):
    """ Clone the content to be translated
    """
    catalog = site.portal_catalog
    english_container = site['en']
    language_folders = [
        x.id for x in catalog.searchResults(path='/cca', portal_type='LRF')]
    language_folders.remove('en')

    # removed 'frontpage-slides' from lang_independent_objects
    lang_independent_objects = [
        "newsletter", "Members", "repository", "test-baltic", "frontpage",
        "admin",  "more-latest-updates", "sandbox", "portal_pdf",
        "portal_vocabularies", "portal_depiction",
        "dashboard", "latest-modifications-on-climate-adapt",
        "covenant-of-mayors-external-website", "rss-feed",
        "latest-news-events-on-climate-adapt",
        "specific-privacy-statement-for-climate-adapt",
        "privacy-and-legal-notice", "database-items-overview", "broken-links",
        "observatory-organisations",
        "observatory-management-group-organisations",
        "indicators-backup", "eea-copyright-notice", "eea-disclaimer",
        "user-dashboard"]

    # move folders under /en/
    for brain in site.getFolderContents():
        obj = brain.getObject()

        if obj.portal_type != 'LRF' and obj.id not in lang_independent_objects:
            content.move(source=obj, target=english_container)

    transaction.commit()
    errors = []
    # get and parse all objects under /en/
    res = get_all_objs(english_container)

    failed_translations = []
    count = 0
    for brain in res:
        logger.info('--------------------------------------------------------')
        logger.info(count)
        count += 1
        if brain.getPath() == '/cca/en' or brain.portal_type == 'LIF':
            continue
        obj = brain.getObject()
        try:
            create_translation_object(obj, language)
            logger.info("Cloned: %s" % obj.absolute_url())
        except Exception as err:
            logger.info("Error cloning: %s" % obj.absolute_url())
            if err.message == 'Translation already exists':
                continue
            else:
                errors.append(obj)
                # import pdb; pdb.set_trace()

        if count % 200 == 0:
            logger.info("Processed %s objects" % count)
            transaction.commit()

    transaction.commit()
    logger.info("Errors")
    logger.info(errors)
    logger.info("Finished cloning for language %s" % language)

    return 'Finished cloning for language %s' % language


def verfiy_unlinked_translation(site, request):
    """ Clone the content to be translated if not exist
    """
    language = request.get('language', None)
    available_languages = ['es','de','it','pl','fr']
    check_nr_languages = request.get('check_nr_languages', len(available_languages)+1)
    uid = request.get('uid', None)
    limit = int(request.get('limit', 0))
    offset = int(request.get('offset', 0))
    portal_type = request.get('portal_type', None)

    catalog = site.portal_catalog
    language_container = site['en']

    # get and parse all objects under /en/
    res = get_all_objs(language_container)

    failed_translations = []
    count = 0
    for brain in res:
        obj = brain.getObject()

        if uid and uid != brain.UID:
            continue
        if portal_type and portal_type!=obj.portal_type:
            continue

        translations = TranslationManager(obj).get_translations()

        if len(translations)<check_nr_languages:
            logger.info(obj.absolute_url())
            for available_language in available_languages:
                create_translation_object(obj, available_language)


def report_unlinked_translation(site, request):
    """ Report untranslated items
    """
    language = request.get('language', None)
    available_languages = ['es','de','it','pl','fr']
    check_nr_languages = request.get('check_nr_languages', len(available_languages)+1)
    uid = request.get('uid', None)
    limit = int(request.get('limit', 0))
    offset = int(request.get('offset', 0))
    portal_type = request.get('portal_type', None)

    catalog = site.portal_catalog
    language_container = site['en']
    #import pdb; pdb.set_trace()

    response = []
    # get and parse all objects under /en/
    brains = get_all_objs(language_container)

    failed_translations = []
    count = 0
    for brain in brains:
        obj = brain.getObject()

        if uid and uid != brain.UID:
            continue
        if portal_type and portal_type!=obj.portal_type:
            continue

        translations = TranslationManager(obj).get_translations()
        #import pdb; pdb.set_trace()

        #logger.info('--------------------------------------------------------')
        #logger.info(count)

        if len(translations)<check_nr_languages:
            response.append(obj.absolute_url())

    return response


def admin_some_translated(site, items):
    """ Create a list of links to be tested (for translation) for each
        content type
    """
    items = int(items)
    catalog = site.portal_catalog
    portal_types = []
    links = {}
    fields = {}

    res = catalog.searchResults(path='/cca/en')
    count = -1
    for brain in res:
        count += 1
        logger.info(count)
        obj = brain.getObject()

        portal_type = obj.portal_type
        if portal_type not in portal_types:
            portal_types.append(portal_type)
            links[portal_type] = []

            # get behavior fields and values
            behavior_assignable = IBehaviorAssignable(obj)
            _fields = {}
            if behavior_assignable:
                behaviors = behavior_assignable.enumerateBehaviors()
                for behavior in behaviors:
                    for k, v in getFieldsInOrder(behavior.interface):
                        _fields.update({k: v})

            #  get schema fields and values
            for k, v in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
                _fields.update({k: v})

            fields[portal_type] = [(x, _fields[x]) for x in _fields]

        if len(links[portal_type]) < items:
            links[portal_type].append(obj.absolute_url())

    return {'Content types': portal_types, 'Links': links, 'fields': fields}


class PrepareTranslation(BrowserView):
    """ Clone the content to be available for a new translation
        Usage: /admin-prepare-translation?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return execute_trans_script(getSite(), **kwargs)


class VerfiyUnlinkedTranslation(BrowserView):
    """ Check items which does not have relation to english
        Usage: /admin-verify-unlinked-translation
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verfiy_unlinked_translation(getSite(), self.request)


class ReportUnlinkedTranslation(BrowserView):
    """ Check items which does not have relation to english
        Usage: /admin-report-unlinked-translation
    """

    def report(self, **kwargs):
        kwargs.update(self.request.form)
        return report_unlinked_translation(getSite(), self.request)


class VerifyClonedLanguage(BrowserView):
    """ Use this view to check all links for a new cloned language
        Usage: /admin-verify-cloned?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_cloned_language(getSite(), **kwargs)


class VerifyTranslationFields(BrowserView):
    """ Use this view to check all links for a new cloned language
        Usage: /admin-verify-translation-fields?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_translation_fields(getSite(), self.request)


class TranslateStep1(BrowserView):
    """ Use this view to get a json files for all eng objects
        Usage: /admin-translate-step-1?limit=10&search_path=some-words-in-url
        Limit and search_path params are optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_1(getSite(), self.request)


class TranslateStep2(BrowserView):
    """ Use this view to translate all json files to a language
        Usage: /admin-translate-step-2-old?language=ro&uid=ABCDEF
        uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_2(getSite(), self.request)


class TranslateStep3(BrowserView):
    """ Use this view to save the values from annotation in objects fields
        Usage: /admin-translate-step-3?language=ro&uid=ABCDEF
        uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_3(getSite(), self.request)


class TranslateStep4(BrowserView):
    """ Use this view to copy fields values that are language independent
        Usage: /admin-translate-step-4?language=ro&uid=ABCDEF
        uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_4(getSite(), self.request)


class TranslateRepaire(BrowserView):
    """ Use this view to save the values from annotation in objects fields
        Usage: /admin-translate-repaire?language=es&file=ABCDEF
        file : /tmp/[ABCDEF].json
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_repaire(getSite(), self.request)

class TranslateRepaireStep3(BrowserView):
    """ Use this view to save the values from annotation in objects fields
        Usage: /admin-translate-repaire-step-3?language=es&file=ABCDEF
        file : /tmp/[ABCDEF].json
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_repaire_step_3(getSite(), self.request)


class TranslationListTypeFields(BrowserView):
    """ Use this view to translate all json files to a language
        Usage: /admin-translate-step-2?language=ro
    """

    def __call__(self, **kwargs):
        return translation_list_type_fields(getSite())


class SomeTranslated(BrowserView):
    """ Prepare a list of links for each content type in order to verify
        translation
        Usage: /admin-some-translated?items=10
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return admin_some_translated(getSite(), **kwargs)


class RunTranslation(BrowserView):
    """ Translate the contents
        Usage:
        /admin-run-translation?language=it&version=1&skip=1200  -skip 1200 objs
        /admin-run-translation?language=it&version=1
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return initiate_translations(getSite(), **kwargs)


class RunTranslationSingleItem(BrowserView):
    """ Translate a single item
        Usage: item/admin-translate-this

        To be used for testing translation without waiting for all objects to
        be updated
    """

    def __call__(self, **kwargs):
        import pdb; pdb.set_trace()
        obj = self.context
        result = translate_obj(obj)
        transaction.commit()
        return result


class TranslationStatus(BrowserView):
    """ Display the the current versions for all translated objects
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)

        if "version" in kwargs:
            return translations_status_by_version(getSite(), **kwargs)

        return translations_status(getSite(), **kwargs)


class TranslationInfoViewlet(ViewletBase):
    """ Display translation info for current object
    """
    def get_language(self):
        return get_current_language(self.context, self.request)

    def is_translated_content(self):
        obj_language = self.get_language()
        if obj_language == "en":
            return False

        translations = TranslationManager(self.context).get_translations()
        trans_obj = translations.get(obj_language)
        if trans_obj is not None:
            url = trans_obj.absolute_url()
            actual_url = self.request.get("ACTUAL_URL")
            if url == actual_url:
                return True

            if "folder_contents" in actual_url:
                return False

            return True

        return False


class TranslationStateViewlet(ViewletBase):
    """ Display the translation state
    """
    trans_wf_id = 'cca_translations_workflow'
    css_types = {
        'not_translated': 'error',
        'translation_not_approved': 'warning',
        'translation_approved': 'info',
    }

    def show_approve_button(self):
        context = self.context
        state, wf_state = self._get_current_wf_state(context)

        return state == 'translation_not_approved'

    def get_css_class(self):
        context = self.context
        css_class = "portalMessage {}"
        state, wf_state = self._get_current_wf_state(context)
        css_type = self.css_types.get(state, 'no_state')

        return css_class.format(css_type)

    def _get_current_wf_state(self, context=None):
        if context is None:
            context = self.context

        wftool = get_tool('portal_workflow')
        wf = None

        for _wf in wftool.getWorkflowsFor(context):
            if _wf.id != self.trans_wf_id:
                continue

            wf = _wf

        if not wf:
            return 'Translation state not found', None

        initial_state = wf.initial_state
        state = (wftool.getStatusOf('cca_translations_workflow', self.context)
                    or {})
        state = state.get("review_state", initial_state)
        wf_state = wf.states[state]

        return state, wf_state

    def get_status(self, context=None):
        state, wf_state = self._get_current_wf_state(context)
        title = wf_state and wf_state.title.strip() or state

        return title

    def get_transitions(self, context=None):
        if not context:
            context = self.context

        wftool = get_tool('portal_workflow')
        transitions = wftool.listActionInfos(object=context)

        return [t for t in transitions if t['allowed']]


class TranslationCheckLanguageViewlet(ViewletBase):
    """ Display if we have translation for language set in cookie
    """

    def show_display_message(self):
        #import pdb; pdb.set_trace()
        if self.get_plone_language()!=self.get_cookie_language():
            # check if force to stay on this page
            if self.request.get('langflag', None):
                return True
            url = self.get_suggestion_url()
            # if we have a url, then redirect. A few pages are not translated
            if url:
                return self.request.response.redirect(url)
            return True
        return None

    def get_message(self, message):
        #import pdb; pdb.set_trace()
        return translate_text(self.context, self.request, message, 'eea.cca', self.get_cookie_language())

    def get_plone_language(self):
        #import pdb; pdb.set_trace()
        return get_current_language(self.context, self.request)

    def get_cookie_language(self):
        #import pdb; pdb.set_trace()
        return self.request.cookies.get("I18N_LANGUAGE", "en")

    def get_suggestion_url(self):
        #import pdb; pdb.set_trace()
        #check if cookie plone language is not en
        translations = TranslationManager(self.context).get_translations()
        cookie_language = self.get_cookie_language()
        if cookie_language in translations:
            return translations[cookie_language].absolute_url()
        return None


class AdminPublishItems(BrowserView):
    """ Publish the items needed for frontpage to work 
        news, events, countries-regions
    """
    
    items_to_publish = [
        'frontpage-slides',
        'more-events', 
        'countries-regions', 
        'news-archive', 
        'countries-regions/countries'
    ]

    @property
    def site(self):
        site = portal.getSite()
        
        return site

    @property
    def wftool(self):
        wftool = get_tool('portal_workflow')

        return wftool

    def get_object_by_path(self, path):
        try:
            obj = self.site.restrictedTraverse(path)
        except:
            logger.info("Path not found: %s" % path)                    
            
            return None

        return obj

    def publish_obj(self, obj):
        if api.content.get_state(obj) != "published":
            logger.info("Publishing %s" % obj.absolute_url())
            try:
                self.wftool.doActionFor(obj, 'publish')        
            except:
                return obj.absolute_url()

    def __call__(self):
        errors = []

        for item in self.items_to_publish:
            en_path = "en/{}".format(item)
            obj_en = self.get_object_by_path(en_path)
            
            if not obj_en:
                continue
            
            # skip if english item is not published
            if api.content.get_state(obj_en) != "published":
                continue
            
            translations = TranslationManager(obj_en).get_translations()

            # first step: publish the item
            for language in translations.keys():
                transl_path = "{}/{}".format(language, item)
                obj_transl = self.get_object_by_path(transl_path)

                if not obj_transl:
                    continue
                
                result = self.publish_obj(obj_transl)
                if result:
                    errors.append(result)
                
            # second step: publish the contents of the item
            for title, content_obj in obj_en.contentItems():
                try:
                    if api.content.get_state(content_obj) != "published":
                        continue
                except:
                    continue

                translations = TranslationManager(content_obj).get_translations()

                for _lang, _obj_transl in translations.items():
                    result = self.publish_obj(_obj_transl) 

                    if result:
                        errors.append(result)

        return "<br>".join(errors)

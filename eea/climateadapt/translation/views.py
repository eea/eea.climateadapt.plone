""" Translation views
"""
import logging
import base64
import os

from zope import event

from bs4 import BeautifulSoup
from eea.cache.event import InvalidateMemCacheEvent
from Products.Five.browser import BrowserView

from . import (normalize, save_translation, get_translation_keys,
               get_translation_key_values, get_translation_report)
from .interfaces import ITranslationContext

from plone.api import portal
from eea.climateadapt.browser.admin import force_unlock
from plone.app.textfield.value import RichTextValue
from eea.climateadapt.translation.admin import get_translation_object_from_uid

logger = logging.getLogger('wise.msfd.translation')
env = os.environ.get

ANNOTATION_KEY = 'translation.msfd.storage'
TRANS_USERNAME = 'ipetchesi'        # TODO: get another username?
MARINE_PASS = env('MARINE_PASS', '')

SERVICE_URL = 'https://webgate.ec.europa.eu/etranslation/si/translate'


class TranslationCallback(BrowserView):
    """ This view is called by the EC translation service.
    Saves the translation in Annotations (or directly in the object in case
    of html fields).
    """

    def __call__(self):
        form = self.request.form
        if form.get('format', None) == 'html':
            file = self.request.stdin
            self.save_html_fields(form, file)
            logger.info('Translate html')
            return

        if form.get('one_step', None) == "true" and \
                form.get('is_cover', None) != 'true':
            uid = form.get('uid', None)
            trans_obj_path = form.get("external-reference")
            if 'https://' in trans_obj_path:
                site = portal.getSite()
                trans_obj_path = "/cca" + trans_obj_path.split(
                        site.absolute_url())[-1]
            field = form.get('field', None)
            if uid is not None and field is not None:
                form.pop('uid', None)
                form.pop('one_step', None)
                form.pop('request-id', None)
                form.pop('external-reference', None)
                form.pop('target-language', None)
                form.pop('field', None)
                form.pop('source_lang', None)
                translated = form.pop('translation', form.keys()[0]).strip()
                translated = translated.decode('latin-1')
                self.save_text_field(uid, field, translated, trans_obj_path)
            else:
                logger.info("Wrong callback data. Missing uid or field name.")
            return

        if form.get('one_step', None) == "true" and \
                form.get('is_cover', None) == 'true':
            self.save_tile_field(form)
            return

        deps = ['translation']
        event.notify(InvalidateMemCacheEvent(raw=True, dependencies=deps))
        logger.info('Invalidate cache for dependencies: %s', ', '.join(deps))

        logger.info('Translate params all : %r', form)

        form.pop('request-id', None)
        target_language = form.pop('target-language', None)

        language = form.pop('source_lang', None)

        if language is None:
            language = ITranslationContext(self.context).language

        original = form.pop('external-reference', '')
        original = normalize(original)

        logger.info('Translate params all : %r', form)

        translated = form.pop('translation', form.keys()[0]).strip()

        # translated = decode_text(translated)
        # it seems the EC service sends translated text in latin-1.
        # Please double-check, but the decode_text that automatically detects
        # the encoding doesn't seem to do a great job

        translated = translated.decode('latin-1')

        save_translation(original, translated, language, target_language)

        return '<a href="/@@translate-key?key=' + \
            original + '">available translations</a>'

    def save_tile_field(self, form):
        """ Save a simple text filed in a cover tile
        """
        field = form.get('field', None)
        tile_id = form.get('tile_id', None)
        if tile_id is not None and field is not None:
            form.pop('uid', None)
            form.pop('one_step', None)
            form.pop('request-id', None)
            trans_obj_path = form.get("external-reference")
            form.pop('external-reference', None)
            form.pop('target-language', None)
            form.pop('field', None)
            form.pop('source_lang', None)
            form.pop('tile_id', None)
            form.pop('is_cover', None)
            translated = form.pop('translation', form.keys()[0]).strip()
            # translated = translated.decode('latin-1')

            tile_annot_id = 'plone.tiles.data.' + tile_id
            site = portal.getSite()
            if 'https://' in trans_obj_path:
                trans_obj_path = "/cca" + trans_obj_path.split(
                        site.absolute_url())[-1]
            trans_obj = site.unrestrictedTraverse(trans_obj_path)
            tile = trans_obj.__annotations__.get(tile_annot_id, None)

            if not tile:
                return

            try:
                update = tile.data
            except AttributeError:
                update = tile

            translated_msg = translated
            if translated_msg is not None:
                update[field] = translated_msg

            try:
                trans_obj.__annotations__[tile_annot_id] = update
            except Exception as err:
                logger.info("One step: Error on saving translated tile field")
                # import pdb; pdb.set_trace()

    def save_text_field(self, uid, field, value, trans_obj_path):
        """ Save the translated value of given field for specified obj by uid
        """
        site = portal.getSite()
        catalog = site.portal_catalog
        # trans_obj = get_translation_object_from_uid(uid, catalog)
        trans_obj = site.unrestrictedTraverse(trans_obj_path)

        if value is not None:
            force_unlock(trans_obj)
            encoded_text = value.encode('latin-1')
            try:
                setattr(trans_obj, field, encoded_text)
                have_change = True
            except AttributeError:
                logger.info("One step: AttributeError for obj: %s key: %s",
                            trans_obj.absolute_url(), field)
            if have_change:
                trans_obj._p_changed = True
                trans_obj.reindexObject()

            logger.info("One step: saved %s %s %s", uid, field, value)

    def save_html_fields(self, form, file):
        """ Get the translated html file, extract the values for each field and
            update the related translation object.
        """
        site = portal.getSite()
        trans_obj_path = form.get("external-reference")
        if 'https://' in trans_obj_path:
            trans_obj_path = "/cca" + trans_obj_path.split(site.absolute_url())[-1]

        form.pop('format')
        form.pop('request-id')
        form.pop('external-reference')
        source_lang = form.get('source_lang')
        form.pop('source_lang')
        target_lang = form.get('target-language')
        form.pop('target-language')
        # logger.info("Translate %s to %s", source_lang, target_lang)

        trans_obj = site.unrestrictedTraverse(trans_obj_path)
        force_unlock(trans_obj)

        if len(form.keys()) == 0:
            logger.info("Empty form")  # TODO: Check why?
            return
    
        file.seek(0)
        b64_str = file.read()
        html_file = base64.decodestring(b64_str).decode("latin-1")
        # logger.info(html_file)
        soup = BeautifulSoup(html_file, "html.parser")

        html_fields = soup.find_all(
                'div', attrs={"class": "cca-translation-section"})

        for field in html_fields:
            field_name = field['data-field']
            html_value = field.decode_contents()
            encoded_text = html_value.encode('latin-1')
            setattr(trans_obj, field_name, RichTextValue(encoded_text))
            trans_obj._p_changed = True
            trans_obj.reindexObject(idxs=[field_name])

        tiles = soup.find_all(
                'div', attrs={"class": "cca-translation-tile"})

        for field in tiles:
            field_name = field['data-field']
            tile_id = field['data-tile-id']
            html_value = field.decode_contents()
            encoded_text = html_value.encode('latin-1')
            # tile = trans_obj.get_tile(tile_id)
            tile_annot_id = 'plone.tiles.data.' + tile_id
            tile = trans_obj.__annotations__.get(tile_annot_id, None)
            if tile is not None:
                try:
                    update = tile.data
                except AttributeError:
                    update = tile
                update['text'] = RichTextValue(encoded_text)
                # tile.data.update(update)
                trans_obj.__annotations__[tile_annot_id] = update
                # trans_obj.reindexObject()
            else:
                logger.info("Cannot find tile")
        logger.info("Html translation saved for %s", trans_obj.absolute_url())


class TranslationList(BrowserView):
    """ This view is called by the EC translation service.
    Saves the translation in Annotations
    """

    def list(self):
        form = self.request.form
        search = form.get('search', None)
        limit = int(form.get('limit', 10))

        data = get_translation_keys()
        if search:
            data = [item for item in data if  search in item]
        if len(data)>limit:
            data=data[0:limit]
        return data

    def keys(self):
        key = self.request.form["key"]
        return get_translation_key_values(key)

    def report(self):
        return get_translation_report()

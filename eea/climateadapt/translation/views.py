""" Translation views
"""
import logging
import base64
import os

from zope import event

from bs4 import BeautifulSoup
from eea.cache.event import InvalidateMemCacheEvent
from Products.Five.browser import BrowserView

from . import (normalize, save_translation,
               get_translation_keys, get_translation_key_values)
from .interfaces import ITranslationContext

from plone.api import portal
from eea.climateadapt.browser.admin import force_unlock
from plone.app.textfield.value import RichTextValue

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

    def save_html_fields(self, form, file):
        """ Get the translated html file, extract the values for each field and
            update the related translation object.
        """
        site = portal.getSite()
        obj_path = form.get("external-reference")

        en_obj = site.unrestrictedTraverse(obj_path)
        force_unlock(en_obj)

        form.pop('format')
        form.pop('request-id')
        form.pop('external-reference')
        source_lang = form.get('source_lang')
        form.pop('source_lang')
        target_lang = form.get('target-language')
        form.pop('target-language')
        # logger.info("Translate %s to %s", source_lang, target_lang)

        prefix = '/cca/' + target_lang.lower() + '/'
        trans_obj_path = obj_path.replace('/cca/en/', prefix)
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
            tile = trans_obj.__annotations__.get(
                'plone.tiles.data.' + tile_id, None)
            if tile is not None:
                update = tile.data
                update['text'] = RichTextValue(encoded_text)
                tile.data.update(update)
                trans_obj.reindexObject()
            else:
                logger.info("Cannot find tile")
        logger.info("Html translation saved for %s", trans_obj.absolute_url())


class TranslationList(BrowserView):
    """ This view is called by the EC translation service.
    Saves the translation in Annotations
    """

    def list(self):
        return get_translation_keys()

    def keys(self):
        key = self.request.form["key"]
        return get_translation_key_values(key)

import logging

from zope import event
from zope.security import checkPermission

from eea.cache.event import InvalidateMemCacheEvent
from langdetect.detector import LangDetectException
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as VPTF
from Products.statusmessages.interfaces import IStatusMessage

from . import (delete_translation, get_detected_lang, get_translated,
               normalize, retrieve_translation, save_translation,
               get_translation_keys, get_translation_key_values)
from .interfaces import ITranslationContext

from plone.api import portal

logger = logging.getLogger('wise.msfd.translation')


class TranslationCallback(BrowserView):
    """ This view is called by the EC translation service.
    Saves the translation in Annotations
    """

    def __call__(self):
        deps = ['translation']
        event.notify(InvalidateMemCacheEvent(raw=True, dependencies=deps))
        logger.info('Invalidate cache for dependencies: %s', ', '.join(deps))

        form = self.request.form

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

        return '<a href="/@@translate-key?key='+original+'">available translations</a>'

class TranslationList(BrowserView):
    """ This view is called by the EC translation service.
    Saves the translation in Annotations
    """

    def list(self):
        return get_translation_keys()

    def keys(self):
        key = self.request.form["key"]
        return get_translation_key_values(key)

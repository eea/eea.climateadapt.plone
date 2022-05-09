import logging
import requests

from zope import event
from zope.security import checkPermission

from eea.cache.event import InvalidateMemCacheEvent
from langdetect.detector import LangDetectException
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as VPTF
from Products.statusmessages.interfaces import IStatusMessage

from . import (delete_translation, get_detected_lang, get_translated,
               _get_country_code,
               normalize, retrieve_translation, save_translation,
               get_translation_keys, get_translation_key_values)
from .interfaces import ITranslationContext

from plone.api import portal


from requests.auth import HTTPDigestAuth
import json

logger = logging.getLogger('wise.msfd.translation')

ANNOTATION_KEY = 'translation.msfd.storage'
TRANS_USERNAME = 'ipetchesi'        # TODO: get another username?
# MARINE_PASS = env('MARINE_PASS', '')

# USERNAME/PASSWORD FOR TRANS SERVICE
# Marine_EEA_20180706 : P7n3BLvCerm7cx3B


MARINE_PASS = 'P7n3BLvCerm7cx3B'
SERVICE_URL = 'https://webgate.ec.europa.eu/etranslation/si/translate'

class TranslationCallback(BrowserView):
    """ This view is called by the EC translation service.
    Saves the translation in Annotations
    """

    def __call__(self):
        import pdb; pdb.set_trace()
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

class TestTranslationView(BrowserView):
    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        logger.info('TestTranslationView1')
        #return self.retrieve_translation(**kwargs)

        form = self.request.form
        country_code = form.pop('country_code', None)
        target_languages = form.pop('target_languages', None)
        text = form.pop('text', None)
        force = form.pop('force', False)

        if isinstance(target_languages, str):
            target_languages = target_languages.split(',')

        logger.info('Response translation : %s %s %s %s', country_code, text, target_languages, force)

        return retrieve_translation(country_code, text, target_languages, force)

    def retrieve_translation(self, country_code, text, target_languages=None, force=False):
        """ Send a call to automatic translation service, to translate a string
        Returns a json formatted string
        """
        logger.info('TestTranslationView2')

        country_code = _get_country_code(country_code, text)

        if not text:
            return

        # translation = get_translated(text, country_code)
        #
        # if translation:
        #     if not(force or (u'....' in translation)):
        #         # don't translate already translated strings, it overrides the
        #         # translation
        #         res = {
        #             'transId': translation,
        #             'externalRefId': text,
        #         }
        #
        #         return res

        site_url = portal.get().absolute_url()

        # if 'localhost' in site_url:
        #     logger.warning(
        #         "Using localhost, won't retrieve translation for: %s", text)
        #
        #     return {}

        # if detected language is english skip translation

        if get_detected_lang(text) == 'en':
            logger.info(
                "English language detected, won't retrive translation for: %s",
                text
            )

            return

        if not target_languages:
            target_languages = ['EN']

        dest = '{}/@@translate-callback?source_lang={}'.format(site_url,
                                                               country_code)

        logger.info('Translate callback URL: %s', dest)

        data = {
            'priority': 5,
            'callerInformation': {
                'application': 'Marine_EEA_20180706',
                'username': TRANS_USERNAME,
            },
            'domain': 'SPD',
            'externalReference': text,          # externalReference,
            'textToTranslate': text,
            'sourceLanguage': country_code,
            'targetLanguages': [target_languages],
            'destinations': {
                'httpDestinations':
                [dest],
            }
        }

        logger.info('Data translation request: %r', data)

        resp = requests.post(
            SERVICE_URL,
            auth=HTTPDigestAuth('Marine_EEA_20180706', MARINE_PASS),
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        logger.info('Response from translation request: %r', resp.content)

        res = {
            "transId": resp.content,
            "externalRefId": text
        }
        #import pdb; pdb.set_trace()
        return res

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.multilingual.manager import TranslationManager

from eea.climateadapt.translation import retrieve_translation


class TranslationUtilsMixin(object):
    """ Class with utility methods related to translations """

    @property
    def current_lang(self):
        current_language = get_current_language(self.context, self.request)

        return current_language

    def get_translation_for_text(self, value, language=None):
        if not language:
            language = self.current_lang

        language = language.upper()

        if language == 'EN':
            return value

        translated = retrieve_translation(
            'EN', value, [language])

        if 'translated' in translated:
            encoded_text = translated['transId'].encode(
                    'latin-1')

            return encoded_text

        return value


def get_current_language(context, request):
    context = context.aq_inner
    portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
    return portal_state.language()

def translate_text(context, request, text, domain=u'eea.climateadapt', language=None):
    tool = getToolByName(context, "translation_service")
    if not language:
        language = get_current_language(context, request)

    return tool.translate(text,
            domain=domain,
            target_language=language
            )

def get_site_languages():
    try:
        languages = TranslationManager(
                api.portal.get().restrictedTraverse("en")
                ).get_translations().keys()
        return languages
    except Exception:
        return []

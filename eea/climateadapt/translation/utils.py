import urllib

from eea.climateadapt.translation import retrieve_translation
from plone import api
from plone.app.multilingual.manager import TranslationManager
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


class TranslationUtilsMixin(object):
    """ Class with utility methods related to translations """

    def translated_url(self, url):
        """return the relative url for the object, including the current language
        example for FR

        /metadata/test -> /fr/metadata/test
        /en/metadata/test -> /fr/metadata/test
        """

        replace_urls = [
            'https://cca.devel5cph.eionet.europa.eu',
            'https://climate-adapt.eea.europa.eu'
        ]

        portal_url = self.context.portal_url()

        if portal_url in url:
            relative_path = url.replace(portal_url, '')
        else:
            for r_url in replace_urls:
                url = url.replace(r_url, '')

            relative_path = url

        if relative_path.startswith('/'):
            relative_path = relative_path[1:]

        relative_path_split = relative_path.split('/')

        if relative_path_split[0] == self.current_lang:
            return relative_path

        if relative_path_split[0] == 'en':
            new_path = "/{}/{}".format(
                self.current_lang, relative_path_split[1:].join('/'))

            return new_path

        new_path = "/{}/{}".format(
            self.current_lang, relative_path)

        return new_path

    def translated_object(self, object):
        url = object.absolute_url()
        """return the relative url for the object, including the current language
        example for FR

        /metadata/test -> /fr/metadata/test
        /en/metadata/test -> /fr/metadata/test
        """

        replace_urls = [
            'https://cca.devel5cph.eionet.europa.eu',
            'https://climate-adapt.eea.europa.eu'
        ]

        portal_url = self.context.portal_url()

        if portal_url in url:
            relative_path = url.replace(portal_url, '')
        else:
            for r_url in replace_urls:
                url = url.replace(r_url, '')

            relative_path = url

        if relative_path.startswith('/'):
            relative_path = relative_path[1:]

        relative_path_split = relative_path.split('/')

        if relative_path_split[0] == self.current_lang:
            return relative_path

        if relative_path_split[0] == 'en':
            new_path = "/{}/{}".format(
                self.current_lang, '/'.join(relative_path_split[1:]))

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

    def get_i18n_for_text(self, text, domain=u'eea.climateadapt', language=None):
        if not language:
            language = self.current_lang

        language = language.lower()

        if language == 'en':
            return text

        return translate_text(self.context, self.request, text, domain, language)


def get_current_language(context, request):
    try:
        context = context.aq_inner
        portal_state = getMultiAdapter(
            (context, request), name=u'plone_portal_state')
        return portal_state.language()
    except Exception:
        return 'en'


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


def filters_to_query(args):
    """

    args = [
        ('objectProvides', ACEID_TO_SEARCHTYPE.get(search_type) or search_type),
        ('cca_adaptation_sectors.keyword', "Urban"),
    ]
    """
    res = []
    for i, (name, val) in enumerate(args):
        res.append(['filters[{0}][field]'.format(i), name])
        res.append(['filters[{0}][type]'.format(i), 'any'])
        if isinstance(val, list):
            for x, lv in enumerate(val):
                res.append(['filters[{0}][values][{1}]'.format(i, x), lv])
        else:
            res.append(['filters[{0}][values][0]'.format(i), val])

    return urllib.urlencode(dict(res))

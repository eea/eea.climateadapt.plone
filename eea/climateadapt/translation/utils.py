from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.multilingual.manager import TranslationManager

def get_current_language(context, request):
    context = context.aq_inner
    portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
    return portal_state.language()

def translate_text(context, request, text, domain=u'eea.climateadapt'):
    tool = getToolByName(context, "translation_service")
    current_language = get_current_language(context, request)

    return tool.translate(text,
            domain=domain,
            target_language=current_language
            )

def get_site_languages():
    try:
        languages = TranslationManager(
                api.portal.get().restrictedTraverse("en")
                ).get_translations().keys()
        return languages
    except Exception:
        return []

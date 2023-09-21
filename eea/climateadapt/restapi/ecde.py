# -*- coding: utf-8 -*-
import logging
from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from plone import api
from plone.api import portal
from zope.annotation.interfaces import IAnnotations
from plone.app.multilingual.manager import TranslationManager
from eea.climateadapt.translation.utils import get_current_language

logger = logging.getLogger('eea.climateadapt')


@implementer(IExpandableElement)
@adapter(Interface, IEEAClimateAdaptInstalled)
class C3SIndicatorsOverview(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_ecde_context(self):
        if 'european-climate-data-explorer' in self.request["ACTUAL_URL"]:
            return True
        return False

    def get_indicators_data(self):
        res = {'description': '', 'items': []}

        url = self.request["ACTUAL_URL"]
        category = url.split("/")[-2]
        category_id = category.lower().replace("-", " ")
        # category_path = category.lower()

        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.searchResults(
            portal_type='eea.climateadapt.c3sindicator', c3s_theme=category.capitalize())

        items = {}
        for brain in brains:
            if '/en/' not in brain.getURL():
                continue
            obj = brain.getObject()
            items[obj.title] = {
                "url": brain.getURL(),
                "obj": obj
            }

        current_lang = get_current_language(self.context, self.request)

        site = portal.get()
        base_folder = site["en"]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get('c3s_json_data', {})
        res['description'] = datastore['data']['themes'][category_id]['description']
        for indicator in datastore['data']['themes'][category_id]['apps']:
            if indicator['title'] in items:
                obj = items[indicator['title']]['obj']
                if current_lang != 'en':
                    try:
                        translations = TranslationManager(
                            obj).get_translations()
                        if self.current_lang in translations:
                            obj = translations[self.current_lang]
                    except Exception:
                        logger.info(
                            'At least one language is not published for '.obj.absolute_url())
                res['items'].append({
                    'title': obj.title,
                    'url': obj.absolute_url(),
                })
        return res

    def __call__(self):
        if self.is_ecde_context() is True:
            indicators_data = self.get_indicators_data()
        else:
            indicators_data = 'Error: Wrong context.'
        return {"c3s_indicators_overview": indicators_data}


class C3SIndicatorsOverviewGet(Service):
    def reply(self):
        indicators = C3SIndicatorsOverview(self.context, self.request)
        return indicators()

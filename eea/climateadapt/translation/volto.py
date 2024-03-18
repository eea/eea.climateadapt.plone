"""Utilities to convert to streamlined HTML and from HTML to volto blocks

The intention is to use eTranslation as a service to translate a complete Volto page with blocks
by first converting the blocks to HTML, then ingest and convert that structure back to Volto blocks
"""

# from langdetect import language
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.interfaces import IRichText
from plone.app.multilingual.factory import DefaultTranslationFactory
from zope.schema import getFieldsInOrder
from plone.dexterity.utils import iterSchemata
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField

from Products.Five.browser import BrowserView

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from utils import get_value_representation

from eea.climateadapt.translation.utils import get_site_languages
from eea.climateadapt.asynctasks.utils import get_async_service
from .core import (
    create_translation_object,
    execute_translate_async,
)
from plone.app.multilingual.manager import TranslationManager

import logging
import requests
import json
import copy

from zope.component import getMultiAdapter

logger = logging.getLogger("eea.climateadapt")

SLATE_CONVERTER = "http://converter:8000/html"
BLOCKS_CONVERTER = "http://converter:8000/blocks2html"
CONTENT_CONVERTER = "http://converter:8000/html2content"


def get_blocks_as_html(obj):
    data = {"blocks_layout": obj.blocks_layout, "blocks": obj.blocks}
    headers = {"Content-type": "application/json", "Accept": "application/json"}

    req = requests.post(BLOCKS_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    html = req.json()["html"]
    print("html", html)
    return html


def get_content_from_html(html):
    """Given an HTML string, converts it to Plone content data"""

    data = {"html": html}
    headers = {"Content-type": "application/json", "Accept": "application/json"}

    req = requests.post(CONTENT_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    data = req.json()["data"]
    print("data", data)
    return data


class ToHtml(BrowserView):
    def __call__(self):
        obj = self.context

        self.fields = {}
        self.order = []
        self.values = {}

        for schema in iterSchemata(obj):
            for k, v in getFieldsInOrder(schema):
                if (
                    ILanguageIndependentField.providedBy(v)
                    or k in LANGUAGE_INDEPENDENT_FIELDS
                ):
                    continue
                # print(schema, k, v)
                self.fields[k] = v
                value = self.get_value(k)
                if value:
                    self.order.append(k)
                    self.values[k] = value

        html = self.index()
        return html


class ContentToHtml(BrowserView):
    """A page to test html marshalling"""

    def copy(self, fielddata):
        language = "de"
        obj = self.context
        tm = TranslationManager(obj)
        translated_object = tm.get_translation(language)

        if translated_object is None:
            factory = DefaultTranslationFactory(obj)
            translated_object = factory(language)
            tm.register_translation(language, translated_object)

        # from plone import api
        # site = api.portal.get()
        # sandbox = site.restrictedTraverse("sandbox")
        # copy = api.content.copy(source=self.context, target=sandbox)
        # __import__("pdb").set_trace()
        copy = translated_object

        for schema in iterSchemata(obj):
            for k, v in getFieldsInOrder(schema):
                if (
                    ILanguageIndependentField.providedBy(v)
                    or k in LANGUAGE_INDEPENDENT_FIELDS
                    or k not in fielddata
                ):
                    continue
                # print(schema, k, v)
                value = fielddata[k]
                if IRichText.providedBy(v):
                    value = RichTextValue(value)
                setattr(copy, k, value)

        # for k, v in fielddata.items():

        return copy

    def __call__(self):
        obj = self.context
        html = getMultiAdapter(self.context, self.request, name="tohtml")

        if self.request.form.get("half"):
            return html

        if self.request.form.get("full"):
            http_host = self.context.REQUEST.environ["HTTP_X_FORWARDED_HOST"]
            translate_volto_html(html, obj, http_host)
            return html

        data = get_content_from_html(html)

        # because the blocks deserializer returns {blocks, blocks_layout} and is saved in "blocks", we need to fix it
        if data.get("blocks"):
            blockdata = data["blocks"]
            data["blocks_layout"] = blockdata["blocks_layout"]
            data["blocks"] = blockdata["blocks"]

        # json.dumps({"html": html, "data": data}, indent=2)
        url = "http://localhost:3000/" + self.copy(data).absolute_url(
            relative=1
        ).replace("cca/", "")
        return self.request.response.redirect(url)

    def get_value(self, name):
        if name == "blocks":
            return get_blocks_as_html(self.context)
        return get_value_representation(self.context, name)


def translate_volto_html(html, en_obj, http_host):
    """Input: html (generated from volto blocks and obj fields, as string)
           en_obj - the object to be translated
           http_host - website url

    Make sure translation objects exists and request a translation for
    all languages.
    """
    options = {}
    options["obj_url"] = en_obj.absolute_url()
    options["uid"] = en_obj.UID()
    options["http_host"] = http_host
    options["is_volto"] = True
    options["html_content"] = html

    if "/en/" in en_obj.absolute_url():
        # run translate FULL (all languages)
        for language in get_site_languages():
            if language == "en":
                continue

            create_translation_object(en_obj, language)

            translations = TranslationManager(en_obj).get_translations()
            trans_obj = translations[language]
            trans_obj_url = trans_obj.absolute_url()
            trans_obj_path = "/cca" + trans_obj_url.split(http_host)[-1]
            options["trans_obj_path"] = trans_obj_path

            request_vars = {
                # 'PARENTS': obj.REQUEST['PARENTS']
            }
            async_service = get_async_service()
            queue = async_service.getQueues()[""]
            async_service.queueJobInQueue(
                queue,
                ("translate",),
                execute_translate_async,
                en_obj,
                copy.deepcopy(options),
                language,
                request_vars,
            )

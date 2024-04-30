"""Utilities to convert to streamlined HTML and from HTML to volto blocks

The intention is to use eTranslation as a service to translate a complete Volto page with blocks
by first converting the blocks to HTML, then ingest and convert that structure back to Volto blocks
"""

# from langdetect import language
import copy
import json
import logging

import requests
from lxml.html import builder as E
from lxml.html import fragments_fromstring, tostring
from plone.api import portal
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from plone.dexterity.utils import iterSchemata
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder

from eea.climateadapt.asynctasks.utils import get_async_service
from eea.climateadapt.translation.utils import get_site_languages

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from .core import execute_translate_async, save_field_data
from .utils import get_value_representation

# create_translation_object,

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
    logger.info("Blocks converted to html: %s", html)
    return html


def elements_to_text(children):
    return unicode("").join(tostring(f).decode("utf-8") for f in children)


def convert_richtext_to_fragments(mayberichtextvalue):
    if mayberichtextvalue and mayberichtextvalue.raw:
        return fragments_fromstring(mayberichtextvalue.raw)
    return []


def get_cover_as_html(obj):
    elements = []
    unwrapped = obj.aq_inner.aq_self
    annot = getattr(unwrapped, "__annotations__", None)
    m = "plone.tiles.data"

    if annot:
        for k in annot.keys():
            if k.startswith(m):
                attribs = {"data-tile-id": k[len(m) + 1 :]}
                children = []
                data = annot[k]
                if data.get("title"):
                    title = data.get("title")
                    if not isinstance(title, unicode):
                        title = title.decode("utf-8")
                    try:
                        d = {"data-tile-field": "title"}
                        children.append(E.DIV(title, **d))
                    except:
                        __traceback_info__ = ("Wrong value for XML", str(title))

                if data.get("text"):
                    frags = convert_richtext_to_fragments(data["text"])
                    d = {"data-tile-field": "text", "data-tile-type": "richtext"}
                    children.append(E.DIV(*frags, **d))

                div = E.DIV(*children, **attribs)
                elements.append(div)

    return elements_to_text(elements)


def get_content_from_html(html):
    """Given an HTML string, converts it to Plone content data"""

    # removing the cover_layout fragment, as it needs to be treated specially
    # etree = document_fromstring(html)
    # cover_layout = etree.find(".//div[@data-field='cover_layout']")
    # if cover_layout:
    #     cover_layout.getparent().remove(cover_layout)

    data = {"html": html}
    headers = {"Content-type": "application/json", "Accept": "application/json"}

    req = requests.post(CONTENT_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    data = req.json()["data"]
    logger.info("Data from converter: %s", data)

    # because the blocks deserializer returns {blocks, blocks_layout} and is saved in "blocks", we need to fix it
    if data.get("blocks"):
        blockdata = data["blocks"]
        data["blocks_layout"] = blockdata["blocks_layout"]
        data["blocks"] = blockdata["blocks"]

    # __import__('pdb').set_trace()
    if data.get("cover_layout"):
        frags = fragments_fromstring(data["cover_layout"])
        tiles = {}
        for frag in frags:
            # <div data-tile-id=".b3898bdb-017c-4dac-a2d4-556d59d0ea6d"><div data-tile-field="text">
            id = frag.get("data-tile-id")
            info = {}

            for child in frag:
                fieldname = child.get("data-tile-field")
                isrichtext = child.get("data-tile-type") == "richtext"
                if isrichtext:
                    info[fieldname] = elements_to_text(child)
                else:
                    info[fieldname] = child.text
            tiles[id] = info

        data["cover_layout"] = tiles

    logger.info("Data with tiles decrypted %s", data)

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
                self.fields[k] = v
                value = self.get_value(k)
                if value:
                    self.order.append(k)
                    self.values[k] = value

        html = self.index()
        return html

    def get_value(self, name):
        if name == "blocks":
            return get_blocks_as_html(self.context)
        if name == "cover_layout":
            value = get_cover_as_html(self.context)
            return value
        return get_value_representation(self.context, name)


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

        save_field_data(obj, translated_object, fielddata)

        return translated_object

    def __call__(self):
        obj = self.context
        html = getMultiAdapter((self.context, self.request), name="tohtml")()

        if self.request.form.get("half"):
            return html

        if self.request.form.get("full"):
            # This triggers the actual async-callback process to translate
            http_host = self.context.REQUEST.environ.get(
                "HTTP_X_FORWARDED_HOST", portal.get().absolute_url()
            )
            translate_volto_html(html, obj, http_host)
            return html

        data = get_content_from_html(html)

        # json.dumps({"html": html, "data": data}, indent=2)
        url = "http://localhost:3000/" + self.copy(data).absolute_url(
            relative=1
        ).replace("cca/", "")
        return self.request.response.redirect(url)


def translate_volto_html(html, en_obj, http_host):
    """The "new" method of triggering the translation of an object.

    While this is named "volto", it is a generic system to translate Plone
    content. The actual "ingestion" of translated data is performed in the
    TranslationCallback view

    Input: html (generated from volto blocks and obj fields, as string)
           en_obj - the object to be translated
           http_host - website url

    Makes sure translation objects exists and requests a translation for
    all languages.
    """

    options = {
        "obj_url": en_obj.absolute_url(),
        "uid": en_obj.UID(),
        "http_host": http_host,
        "is_volto": True,
        "html_content": html,
    }
    en_obj_path = "/".join(en_obj.getPhysicalPath())

    logger.info("Called translate_volto_html for %s" % en_obj_path)

    if "cca/en" in en_obj_path:
        for language in get_site_languages():
            if language == "en":
                continue
            async_service = get_async_service()
            queue = async_service.getQueues()[""]
            async_service.queueJobInQueue(
                queue,
                ("translate",),
                execute_translate_async,
                en_obj,
                copy.deepcopy(options),
                language,
            )

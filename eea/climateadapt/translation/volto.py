""" Utilities to convert to streamlined HTML and from HTML to volto blocks

The intention is to use eTranslation as a service to translate a complete Volto page with blocks
by first converting the blocks to HTML, then ingest and convert that structure back to Volto blocks
"""

from zope.schema import getFieldsInOrder
from plone.dexterity.utils import iterSchemata
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone import api

from Products.Five.browser import BrowserView

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from utils import get_value_representation

import logging
import requests
import json

logger = logging.getLogger("eea.climateadapt")

SLATE_CONVERTER = "http://converter:8000/html"
BLOCKS_CONVERTER = "http://converter:8000/blocks2html"
CONTENT_CONVERTER = "http://converter:8000/html2content"


def get_blocks_as_html(obj):
    data = {"blocks_layout": obj.blocks_layout, "blocks": obj.blocks}
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}

    req = requests.post(
        BLOCKS_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    html = req.json()["html"]
    print("html", html)
    return html


def get_content_from_html(html):
    data = {"html": html}
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}

    req = requests.post(CONTENT_CONVERTER,
                        data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    data = req.json()["data"]
    print("data", data)
    return data


class ContentToHtml(BrowserView):
    """A page to test html marshalling"""

    def copy(self, fielddata):
        site = api.portal.get()
        sandbox = site.restrictedTraverse("sandbox")
        copy = api.content.copy(source=self.context, target=sandbox)
        for k, v in fielddata.items():
            setattr(copy, k, v)

        return copy

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
                print(schema, k, v)
                self.fields[k] = v
                value = self.get_value(k)
                if value:
                    self.order.append(k)
                    self.values[k] = value

        html = self.index()
        data = get_content_from_html(html)

        # because the blocks deserializer returns {blocks, blocks_layout} and is saved in "blocks", we need to fix it
        if data.get("blocks"):
            blockdata = data["blocks"]
            data["blocks_layout"] = blockdata["blocks_layout"]
            data["blocks"] = blockdata["blocks"]

        # json.dumps({"html": html, "data": data}, indent=2)
        return "http://localhost:3000/" + self.copy(data).absolute_url(relative=1)

    def get_value(self, name):
        if name == "blocks":
            return get_blocks_as_html(self.context)
        return get_value_representation(self.context, name)

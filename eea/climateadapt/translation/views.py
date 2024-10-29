"""Translation views"""

import base64
import cgi
import logging
import os

import transaction
from plone.api import portal
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.dexterity.utils import iterSchemata
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder

from eea.climateadapt.browser.admin import force_unlock
from eea.climateadapt.translation.contentrules import (
    queue_translate_volto_html,
)

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from .core import get_blocks_as_html, ingest_html
from .utils import get_value_representation

logger = logging.getLogger("eea.climateadapt.translation")
env = os.environ.get


class HTMLIngestion(BrowserView):
    """A special view to allow manually submit an HTML translated by
    eTranslation, but that wasn't properly submitted through the callback"""

    def __call__(self):
        html = self.request.form.get("html", "").decode("utf-8")
        path = self.request.form.get("path", "")

        if not (html and path):
            return self.index()

        site = portal.getSite()
        trans_obj = site.unrestrictedTraverse(path)
        ingest_html(trans_obj, html)
        return "ok"


class TranslationCallback(BrowserView):
    """This view is called by the EC translation service.
    Saves the translation in Annotations (or directly in the object in case
    of html fields).
    """

    def __call__(self):
        # for some reason this request acts strange
        qs = self.request["QUERY_STRING"]
        parsed = cgi.parse_qs(qs)
        form = {}
        for name, val in parsed.items():
            form[name] = val[0]

        _file = self.request._file.read()
        logger.info("Translation Callback Incoming form: %s" % form)
        logger.info("Translation Callback Incoming file: %s" % _file)

        self.save_html_volto(form, _file)
        return "ok"

    def save_html_volto(self, form, b64_str):
        # file.seek(0)
        # b64_str = file.read()
        html_translated = base64.decodestring(b64_str).decode("latin-1")

        logger.info("Translate volto html form: %s", form)
        logger.info("Translate volto html: %s", html_translated)

        site = portal.getSite()
        trans_obj_path = form.get("external-reference")
        if "https://" in trans_obj_path:
            trans_obj_path = "/cca" + trans_obj_path.split(site.absolute_url())[-1]

        trans_obj = site.unrestrictedTraverse(trans_obj_path)
        html = html_translated.encode("latin-1")
        ingest_html(trans_obj, html)

        logger.info("Html volto translation saved for %s", trans_obj.absolute_url())


class TranslateObjectAsync(BrowserView):
    def __call__(self):
        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        obj = self.context
        force_unlock(obj)
        html = getMultiAdapter((self.context, self.context.REQUEST), name="tohtml")()
        site = portal.getSite()
        http_host = self.context.REQUEST.environ.get(
            "HTTP_X_FORWARDED_HOST", site.absolute_url()
        )
        language = self.request.form.get("language", None)

        queue_translate_volto_html(html, obj, http_host, language)

        self.request.response.redirect(obj.absolute_url())


class TranslateFolderAsync(BrowserView):
    """Exposed in /see_folder_objects"""

    def __call__(self):
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath())
        )
        site = portal.getSite()
        site_url = site.absolute_url()
        language = self.request.form.get("language", None)

        for i, brain in enumerate(brains):
            obj = brain.getObject()

            logger.info("Queuing %s for translation", obj.absolute_url())
            html = getMultiAdapter((obj, self.context.REQUEST), name="tohtml")()
            http_host = self.context.REQUEST.environ.get(
                "HTTP_X_FORWARDED_HOST", site_url
            )

            force_unlock(obj)
            queue_translate_volto_html(html, obj, http_host, language)

            # if i % 20 == 0:
            #     transaction.commit()

        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")
        self.request.response.redirect(self.context.absolute_url())


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
        # TODO: remove cover_layout related handling
        if name == "cover_layout":
            return None
        #     value = get_cover_as_html(self.context)
        #     return value
        return get_value_representation(self.context, name)

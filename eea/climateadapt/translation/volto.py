"""Utilities to convert to streamlined HTML and from HTML to volto blocks

The intention is to use eTranslation as a service to translate a complete Volto page with blocks
by first converting the blocks to HTML, then ingest and convert that structure back to Volto blocks
"""

# from langdetect import language
import logging

from plone.api import portal
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from .core import (
    get_content_from_html,
    save_field_data,
)
from .contentrules import queue_translate_volto_html

logger = logging.getLogger("eea.climateadapt")


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
            queue_translate_volto_html(html, obj, http_host)
            return html

        data = get_content_from_html(html)

        # json.dumps({"html": html, "data": data}, indent=2)
        url = "http://localhost:3000/" + self.copy(data).absolute_url(
            relative=1
        ).replace("cca/", "")
        return self.request.response.redirect(url)

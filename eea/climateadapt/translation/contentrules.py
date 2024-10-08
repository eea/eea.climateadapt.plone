import copy
import logging
import os

import transaction
from OFS.SimpleItem import SimpleItem
from plone import api
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.app.multilingual.manager import TranslationManager
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from Products.CMFCore.utils import getToolByName
from zope.component import adapter, adapts, getMultiAdapter
from zope.interface import Interface, implementer, implements

from eea.climateadapt.asynctasks.utils import get_async_service
from eea.climateadapt.translation.utils import get_site_languages

from .core import execute_translate_async

logger = logging.getLogger("eea.climateadapt")


def queue_translate_volto_html(html, en_obj, http_host, language=None):
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
    languages = language and [language] or get_site_languages()

    if "cca/en" in en_obj_path:
        for language in languages:
            if language == "en":
                continue
            async_service = get_async_service()
            queue = async_service.getQueues()[""]
            async_service.queueJobInQueue(
                queue,
                ("translate",),
                execute_translate_async,
                en_obj,
                en_obj_path,
                copy.deepcopy(options),
                language,
            )


class ITranslateAction(Interface):
    """Interface for the configurable aspects of a translate action."""


@implementer(ITranslateAction, IRuleElementData)
class TranslateAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.Translate"
    summary = unicode("Translate object")


class TranslateAddForm(NullAddForm):
    """A translate action form"""

    def create(self):
        return TranslateAction()


class TranslateAsyncAddForm(NullAddForm):
    """A translate async action form"""

    def create(self):
        return TranslateAsyncAction()


class ITranslateAsyncAction(Interface):
    """Interface for run translate and translate_step_4 for and object"""


class TranslateAsyncAction(SimpleItem):
    """Async translate and translate_step_4 for and object"""

    implements(ITranslateAsyncAction, IRuleElementData)

    element = "eea.climateadapt.TranslateAsync"
    summary = unicode("Translate object async")


class TranslateAsyncActionExecutor(object):
    """Translate async executor"""

    implements(IExecutable)
    adapts(Interface, ITranslateAsyncAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    @property
    def async_service(self):
        return get_async_service()

    def __call__(self):
        if not os.environ.get("TRANSLATE_ON_CHANGE"):
            logger.warn(
                "TranslateAsyncActionExecutor executed on the wrong server")
            return True

        obj = self.event.object
        html = getMultiAdapter((obj, obj.REQUEST), name="tohtml")()
        site = api.portal.get()
        http_host = self.context.REQUEST.environ.get(
            "HTTP_X_FORWARDED_HOST", site.absolute_url()
        )

        # this will schedule several async jobs that call etranslation async
        queue_translate_volto_html(html, obj, http_host)

        return True


class ISynchronizeStatesForTranslationsAction(Interface):
    """Interface for sync states for translation items action."""


@implementer(ISynchronizeStatesForTranslationsAction, IRuleElementData)
class SynchronizeStatesForTranslationsAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.SynchronizeStatesForTranslations"
    summary = unicode("Synchronize states for translations")


@adapter(Interface, ISynchronizeStatesForTranslationsAction, Interface)
@implementer(IExecutable)
class SynchronizeStatesForTranslationsActionExecutor(object):
    """Make sure the translated objects have the same state as EN object"""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def set_new_state(self, trans_obj, action):
        """Set the new state"""
        try:
            wftool = getToolByName(trans_obj, "portal_workflow")
            wftool.doActionFor(trans_obj, action)
            transaction.commit()
        except Exception:
            logger.info("Synchronize states: not saved for trans object.")

    def __call__(self):
        obj = self.event.object

        if "/en/" in obj.absolute_url():
            logger.info("Synchronize states...")
            action = self.event.action
            translations = TranslationManager(obj).get_translations()
            translated_objs = [translations[x]
                               for x in translations if x != "en"]

            for trans_obj in translated_objs:
                self.set_new_state(trans_obj, action)
        else:
            logger.info("Synchronize states: no action.")

        return True


class SynchronizeStatesForTranslationsAddForm(NullAddForm):
    """A translate action form"""

    def create(self):
        return SynchronizeStatesForTranslationsAction()

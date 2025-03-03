import logging
import os

import transaction
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.app.multilingual.manager import TranslationManager
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from Products.CMFCore.utils import getToolByName
from zope.component import adapter, adapts  # , getMultiAdapter
from zope.interface import Interface, implementer

from .core import queue_translate_volto_html


logger = logging.getLogger("eea.climateadapt")


class TranslateAsyncAddForm(NullAddForm):
    """A translate async action form"""

    def create(self):
        return TranslateAsyncAction()


class ITranslateAsyncAction(Interface):
    """Interface for run translate and translate_step_4 for and object"""


@implementer(ITranslateAsyncAction, IRuleElementData)
class TranslateAsyncAction(SimpleItem):
    """Async translate and translate_step_4 for and object"""

    element = "eea.climateadapt.TranslateAsync"
    summary = str("Translate object async")


@implementer(IExecutable)
class TranslateAsyncActionExecutor(object):
    """Translate async executor"""

    adapts(Interface, ITranslateAsyncAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        if not os.environ.get("TRANSLATE_ON_CHANGE"):
            logger.warn("TranslateAsyncActionExecutor executed on the wrong server")
            return True

        queue_translate_volto_html(self.event.object)
        return True


class ISynchronizeStatesForTranslationsAction(Interface):
    """Interface for sync states for translation items action."""


@implementer(ISynchronizeStatesForTranslationsAction, IRuleElementData)
class SynchronizeStatesForTranslationsAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.SynchronizeStatesForTranslations"
    summary = str("Synchronize states for translations")


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
            translated_objs = [translations[x] for x in translations if x != "en"]

            for trans_obj in translated_objs:
                self.set_new_state(trans_obj, action)
        else:
            logger.info("Synchronize states: no action.")

        return True


class SynchronizeStatesForTranslationsAddForm(NullAddForm):
    """A translate action form"""

    def create(self):
        return SynchronizeStatesForTranslationsAction()

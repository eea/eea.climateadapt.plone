# -*- coding: utf-8 -*-
"""Content rules"""

import logging

import transaction
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from plone import api
from plone.api.portal import get_tool
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.app.multilingual.manager import TranslationManager
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope.component import adapter, adapts
from zope.interface import Interface, implementer, implements
from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.asynctasks.utils import get_async_service
from zope.component import getMultiAdapter
from eea.climateadapt.translation.volto import translate_volto_html

# from eea.climateadapt.translation.utils import get_site_languages
# from zope.site.hooks import getSite
# from eea.climateadapt.translation.core import (
#     # copy_missing_interfaces,
#     # create_translation_object,
#     # translate_obj,
#     # trans_copy_field_data,
#     # trans_sync_workflow_state,
# )

logger = logging.getLogger("eea.climateadapt")


class IObjectDateExpirationAction(Interface):
    """Interface for the configurable aspects of a archived action."""


@implementer(IObjectDateExpirationAction, IRuleElementData)
class ObjectDateExpirationAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.ObjectDateExpiration"
    summary = _("Set object expiration date")


@adapter(Interface, IObjectDateExpirationAction, Interface)
@implementer(IExecutable)
class ObjectDateExpirationActionExecutor(object):
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        transaction.savepoint()

        try:
            state = api.content.get_state(obj)
            if state == "published":
                obj.setExpirationDate(None)
                obj._p_changed = True
                obj.reindexObject()
            if state == "archived":
                obj.setExpirationDate(DateTime())
                obj._p_changed = True
                obj.reindexObject()

        except Exception as e:
            # self.error(obj, str(e))
            return False

        return True


class ObjectDateExpirationAddForm(NullAddForm):
    """A reindex action form"""

    def create(self):
        return ObjectDateExpirationAction()


class IReindexAction(Interface):
    """Interface for the configurable aspects of a reindex action."""


@implementer(IReindexAction, IRuleElementData)
class ReindexAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.Reindex"
    summary = _("Reindex object")


@adapter(Interface, IReindexAction, Interface)
@implementer(IExecutable)
class ReindexActionExecutor(object):
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object

        transaction.savepoint()

        catalog = get_tool("portal_catalog")

        try:
            catalog.unindexObject(obj)
            catalog.indexObject(obj)
        except ConflictError as err:
            raise err
        except Exception as err:
            self.error(obj, str(err))
            return False

        return True

    def error(self, obj, error):
        """Show error"""
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = utils.pretty_title_or_id(obj, obj)
            message = _(
                "Unable to reindex ${name} as part of content rule 'reindex' action: ${error}",
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")


class ReindexAddForm(NullAddForm):
    """A reindex action form"""

    def create(self):
        return ReindexAction()


class ITranslateAction(Interface):
    """Interface for the configurable aspects of a translate action."""


@implementer(ITranslateAction, IRuleElementData)
class TranslateAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.Translate"
    summary = _("Translate object")


# @adapter(Interface, ITranslateAction, Interface)
# @implementer(IExecutable)
# class TranslateActionExecutor(object):
#     """The executor for this action."""
#
#     def __init__(self, context, element, event):
#         self.context = context
#         self.element = element
#         self.event = event
#
#     def __call__(self):
#         obj = self.event.object
#         if "/en/" in obj.absolute_url():
#             self.create_translations(obj)
#             self.copy_fields(obj)
#             self.translate_obj(obj)
#             self.publish_translations(obj)
#             self.copy_interfaces(obj)  # TODO: delete. It's already included in
#
#             # create_translation_object. It is used here only for testing
#             # on old created content. Example: fixing interfaces for pages
#             # like share-your-info
#
#     def error(self, obj, error):
#         """Show error"""
#         request = getattr(self.context, "REQUEST", None)
#         if request is not None:
#             title = utils.pretty_title_or_id(obj, obj)
#             message = _(
#                 "Unable to translate ${name} as part of content rule "
#                 "'translate' action: ${error}",
#                 mapping={"name": title, "error": error},
#             )
#             IStatusMessage(request).addStatusMessage(message, type="error")
#
#     def create_translations(self, obj):
#         """Make sure all translations (cloned) objs exists for this obj"""
#         transaction.savepoint()
#         translations = TranslationManager(obj).get_translations()
#
#         for language in get_site_languages():
#             if language != "en" and language not in translations:
#                 create_translation_object(obj, language)
#
#         transaction.commit()
#
#     def translate_obj(self, obj):
#         """Send the obj to be translated"""
#         try:
#             translate_obj(obj, one_step=True)
#         except Exception as e:
#             self.error(obj, str(e))
#
#     def copy_interfaces(self, obj):
#         """Copy interfaces from en to translated obj"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             trans_obj = translations[language]
#             copy_missing_interfaces(obj, trans_obj)
#
#     def set_workflow_states(self, obj):
#         """Mark translations as not approved"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             this_obj = translations[language]
#             wftool = getToolByName(this_obj, "portal_workflow")
#             wftool.doActionFor(this_obj, "send_to_translation_not_approved")
#
#     def copy_fields(self, obj):
#         """Run step 4 for this obj"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             if language != "en":
#                 settings = {
#                     "language": language,
#                     "uid": obj.UID(),
#                 }
#                 trans_copy_field_data(getSite(), settings)
#
#     def publish_translations(self, obj):
#         """Run step 5 for this obj"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             if language != "en":
#                 settings = {
#                     "language": language,
#                     "uid": obj.UID(),
#                 }
#                 trans_sync_workflow_state(getSite(), settings)


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
    summary = _("Translate object async")


class TranslateAsyncActionExecutor(object):
    """Translate async executor"""

    implements(IExecutable)
    adapts(Interface, ITranslateAsyncAction, Interface)
    noasync_msg = "No instance for async operations was defined."

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    @property
    def async_service(self):
        return get_async_service()

    def __call__(self):
        obj = self.event.object
        html = getMultiAdapter((obj, obj.REQUEST), name="tohtml")()
        site = api.portal.get()
        http_host = self.context.REQUEST.environ.get(
            "HTTP_X_FORWARDED_HOST", site.absolute_url()
        )

        # this triggers a call to eTranslation, so this process is async
        translate_volto_html(html, obj, http_host)

        return True


class ISynchronizeStatesForTranslationsAction(Interface):
    """Interface for sync states for translation items action."""


@implementer(ISynchronizeStatesForTranslationsAction, IRuleElementData)
class SynchronizeStatesForTranslationsAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.SynchronizeStatesForTranslations"
    summary = _("Synchronize states for translations")


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


# def execute_translate_step_4_async(context, options, language, request_vars):
#     """translate via zc.async"""
#     if not hasattr(context, "REQUEST"):
#         zopeUtils._Z2HOST = options["obj_url"]
#         context = zopeUtils.makerequest(context)
#         context.REQUEST["PARENTS"] = [context]
#
#         for k, v in request_vars:
#             context.REQUEST.set(k, v)
#
#     try:
#         settings = {
#             "language": language,
#             "uid": options["uid"],
#         }
#         res = trans_copy_field_data(context, settings, async_request=True)
#         logger.info("Async translate for object %s", options["obj_url"])
#
#     except Exception as err:
#         # async_service = get_async_service()
#
#         # re-schedule PING on error
#         # schedule = datetime.now(pytz.UTC) + timedelta(hours=4)
#         # queue = async_service.getQueues()['']
#         # async_service.queueJobInQueueWithDelay(
#         #     None, schedule, queue, ('translate',),
#         #     execute_translate_step_4_async, context, options, language, request_vars
#         # )
#
#         # mark the original job as failed
#         return "Translate rescheduled for object %s. " "Reason: %s " % (
#             options["obj_url"],
#             str(err),
#         )
#
#     return res

# -*- coding: utf-8 -*-
""" Content rules
"""
import logging
import pytz
import urllib
from datetime import datetime, timedelta
from plone import api
from plone.api.portal import get_tool
import transaction
from OFS.SimpleItem import SimpleItem
# from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.app.multilingual.manager import TranslationManager
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from Products.CMFPlone import utils
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Testing.ZopeTestCase import utils as zopeUtils
from ZODB.POSException import ConflictError
from zope.component import adapter, adapts, queryUtility, ComponentLookupError
from zope.interface import Interface, implementer, implements
from zope.site.hooks import getSite
from DateTime import DateTime

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.translation.admin import translate_obj
from eea.climateadapt.translation.admin import create_translation_object
from eea.climateadapt.translation.admin import copy_missing_interfaces
from eea.climateadapt.translation.admin import translation_step_4
from eea.climateadapt.translation.utils import get_site_languages
from eea.rdfmarshaller.async import IAsyncService
from eea.rabbitmq.plone.rabbitmq import get_rabbitmq_client_settings
from eea.rabbitmq.plone.rabbitmq import queue_msg


logger = logging.getLogger('eea.climateadapt')


class IObjectDateExpirationAction(Interface):
    """Interface for the configurable aspects of a archived action. """


@implementer(IObjectDateExpirationAction, IRuleElementData)
class ObjectDateExpirationAction(SimpleItem):
    """The actual persistent implementation of the action element. """

    element = "eea.climateadapt.ObjectDateExpiration"
    summary = _(u"Set object expiration date")


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
            if state == 'published':
                obj.setExpirationDate(None)
                obj._p_changed = True
                obj.reindexObject()
            if state == 'archived':
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
    """Interface for the configurable aspects of a reindex action. """


@implementer(IReindexAction, IRuleElementData)
class ReindexAction(SimpleItem):
    """The actual persistent implementation of the action element. """

    element = "eea.climateadapt.Reindex"
    summary = _(u"Reindex object")


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
        """ Show error """
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = utils.pretty_title_or_id(obj, obj)
            message = _(
                u"Unable to reindex ${name} as part of content rule 'reindex' action: ${error}",
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")


class ReindexAddForm(NullAddForm):
    """A reindex action form"""

    def create(self):
        return ReindexAction()


class ITranslateAction(Interface):
    """Interface for the configurable aspects of a translate action. """


@implementer(ITranslateAction, IRuleElementData)
class TranslateAction(SimpleItem):
    """The actual persistent implementation of the action element. """

    element = "eea.climateadapt.Translate"
    summary = _(u"Translate object")


@adapter(Interface, ITranslateAction, Interface)
@implementer(IExecutable)
class TranslateActionExecutor(object):
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        if "/en/" in obj.absolute_url():
            self.create_translations(obj)
            self.copy_fields(obj)
            self.translate_obj(obj)
            self.copy_interfaces(obj)  # TODO: delete. It's already included in
            # create_translation_object. It is used here only for testing
            # on old created content. Example: fixing interfaces for pages
            # like share-your-info

    def error(self, obj, error):
        """ Show error """
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = utils.pretty_title_or_id(obj, obj)
            message = _(
                u"Unable to translate ${name} as part of content rule "
                "'translate' action: ${error}",
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")

    def create_translations(self, obj):
        """ Make sure all translations (cloned) objs exists for this obj
        """
        transaction.savepoint()
        translations = TranslationManager(obj).get_translations()
        for language in get_site_languages():
            if language != "en" and language not in translations:
                create_translation_object(obj, language)
        transaction.commit()

    def translate_obj(self, obj):
        """ Send the obj to be translated
        """
        try:
            result = translate_obj(obj, one_step=True)
        except Exception as e:
            self.error(obj, str(e))

    def copy_interfaces(self, obj):
        """ Copy interfaces from en to translated obj
        """
        translations = TranslationManager(obj).get_translations()
        for language in translations:
            trans_obj = translations[language]
            copy_missing_interfaces(obj, trans_obj)

    def set_workflow_states(self, obj):
        """ Mark translations as not approved
        """
        translations = TranslationManager(obj).get_translations()
        for language in translations:
            this_obj = translations[language]
            wftool = getToolByName(this_obj, "portal_workflow")
            wftool.doActionFor(this_obj, 'send_to_translation_not_approved')

    def copy_fields(self, obj):
        """ Run step 4 for this obj
        """
        translations = TranslationManager(obj).get_translations()
        for language in translations:
            if language != "en":
                settings = {
                    "language": language,
                    "uid": obj.UID(),
                }
                translation_step_4(getSite(), settings)


class TranslateAddForm(NullAddForm):
    """A translate action form"""

    def create(self):
        return TranslateAction()


def get_async_service():
        async_service = queryUtility(IAsyncService)

        return async_service


def execute_translate_sds(context, options, language, request_vars):
    """ translate via zc.async
    """
    if not hasattr(context, 'REQUEST'):
        zopeUtils._Z2HOST = options['obj_url']
        context = zopeUtils.makerequest(context)
        context.REQUEST['PARENTS'] = [context]

        for k, v in request_vars:
            context.REQUEST.set(k, v)

    try:
        settings = {
            "language": language,
            "uid": options['uid'],
        }
        res = translation_step_4(context, settings, async_request=True)
        logger.info("Async translate for object %s", options['obj_url'])

    except Exception as err:
        # async_service = get_async_service()

        # re-schedule PING on error
        # schedule = datetime.now(pytz.UTC) + timedelta(hours=4)
        # queue = async_service.getQueues()['']
        # async_service.queueJobInQueueWithDelay(
        #     None, schedule, queue, ('translate',),
        #     execute_translate_sds, context, options, language, request_vars
        # )

        # mark the original job as failed
        return "Translate rescheduled for object %s. "\
            "Reason: %s " % (
                options['obj_url'],
                str(err))

    return res


class TranslateAsyncAddForm(NullAddForm):
    """A translate async action form"""

    def create(self):
        return TranslateAsyncAction()


class ITranslateAsyncAction(Interface):
    """ Interface for run translate and translate_step_4 for and object
    """


class TranslateAsyncAction(SimpleItem):
    """ Async translate and translate_step_4 for and object
    """
    implements(ITranslateAsyncAction, IRuleElementData)

    element = "eea.climateadapt.TranslateAsync"
    summary = _(u"Translate object async")


class TranslateAsyncActionExecutor(object):
    """ Translate async executor
    """
    implements(IExecutable)
    adapts(Interface, ITranslateAsyncAction, Interface)
    noasync_msg = 'No instance for async operations was defined.'
    
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event
        self._rabbit_config = None

    def ping_RabbitMQ(self, options):
        """ Ping the SDS service via RabbitMQ
        """
        params = {}
        params['language'] = options['language']
        params['uid'] = options['uid']
        encoded_params = urllib.urlencode(params)
        full_url = "%s/%s?%s" % (options['portal_url'],
            options['translate_step'], 
            encoded_params)

        msg = "{}".format(full_url)
        try:
            queue_msg(msg, queue="translate_sds_queue")
        except Exception as err:
            logger.error("Sending '%s' in 'translate_sds_queue' FAILED: %s", msg, err)

    @property
    def rabbit_config(self):
        """ RabbitMQ Config
        """
        if self._rabbit_config is not None:
            return self._rabbit_config

        try:
            self._rabbit_config = get_rabbitmq_client_settings()
        except Exception:
            self._rabbit_config = {}
        return self._rabbit_config   

    @property
    def async_service(self):
        return get_async_service()

    def translate_step_4_sds(self, obj):
        options = {}
        options['obj_url'] = obj.absolute_url()
        options['translate_step'] = 'admin-translate-step-4'
        options['uid'] = obj.UID()
        options['portal_url'] = self.context.absolute_url()
        
        translations = TranslationManager(obj).get_translations()
        
        # check if object has translations
        if 'en' not in translations:
            return True
        
        obj_en = translations.pop('en')
        
        for language in translations:
            settings = {
                "language": language,
                "uid": options['uid'],
            }
            # import pdb; pdb.set_trace()
            # translation_step_4(getSite(), settings)
            # options['language'] = language
            self.translate_sds(options, language)

        return True

    def translate_sds(self, options, language):
        """ Ping the CR/SDS service
        """
        # Use zc.async if available
        if self.async_service is None:
            logger.warn("Can't translate_asyn, plone.app.async not installed!")
            return

        queue = self.async_service.getQueues()['']
        
        request_vars = {}
        
        # request_keys_to_copy = ['_orig_env', 'environ', 'other', 'script']
        # for req_key in request_keys_to_copy:
        #     request_vars[req_key] = getattr(self.context.REQUEST, req_key)

        try:
            self.async_service.queueJobInQueue(queue, ('translate',), execute_translate_sds, self.context, options, language, request_vars)
        except ComponentLookupError:
            logger.info(self.noasync_msg)

    def __call__(self):
        obj = self.event.object
        self.translate_step_4_sds(obj)

        return True
# -*- coding: utf-8 -*-

from plone.api.portal import get_tool
import transaction
from OFS.SimpleItem import SimpleItem
#from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from Products.CMFPlone import utils
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.interface import Interface, implementer

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.translation.admin import translate_obj
from eea.climateadapt.translation.admin import create_translation_object
from eea.climateadapt.translation.utils import get_site_languages


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
        except ConflictError as e:
            raise e
        except Exception as e:
            self.error(obj, str(e))
            return False

        return True

    def error(self, obj, error):
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

        transaction.savepoint()

        for language in get_site_languages():
            if language != "en":
                try:
                    create_translation_object(obj, language)
                except Exception as err:
                    pass
                    # import pdb; pdb.set_trace()

        # import pdb; pdb.set_trace()
        try:
            result = translate_obj(obj)
            wftool = getToolByName(obj, "portal_workflow")
            wftool.doActionFor(obj, 'send_to_translation_not_approved')
        except Exception as e:
            self.error(obj, str(e))
            return False

        transaction.commit()

        return True

    def error(self, obj, error):
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = utils.pretty_title_or_id(obj, obj)
            message = _(
                u"Unable to translate ${name} as part of content rule "
                "'translate' action: ${error}",
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")


class TranslateAddForm(NullAddForm):
    """A translate action form"""

    def create(self):
        return TranslateAction()

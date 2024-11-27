# -*- coding: utf-8 -*-
"""Content rules"""

import logging

import transaction
from DateTime import DateTime
from eea.climateadapt import CcaAdminMessageFactory as _
# from eea.climateadapt.asynctasks.utils import get_async_service
# from eea.climateadapt.translation.volto import translate_volto_html
from OFS.SimpleItem import SimpleItem
from plone import api
from plone.api.portal import get_tool
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.interface import Interface, implementer
# from .translation.contentrules import (
#     TranslateAction,
#     TranslateAsyncAction,
#     SynchronizeStatesForTranslationsAction,
# )  # BBB, don't remove, they're referenced from the database

from eea.climateadapt import CcaAdminMessageFactory as _

logger = logging.getLogger("eea.climateadapt")


class IObjectDateExpirationAction(Interface):
    """Interface for the configurable aspects of a archived action."""


@implementer(IObjectDateExpirationAction, IRuleElementData)
class ObjectDateExpirationAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "eea.climateadapt.ObjectDateExpiration"
    summary = str("Set object expiration date")


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

        except Exception:
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
    summary = str("Reindex object")


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
                str(
                    "Unable to reindex ${name} as part of content rule 'reindex' action: ${error}"
                ),
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")


class ReindexAddForm(NullAddForm):
    """A reindex action form"""

    def create(self):
        return ReindexAction()

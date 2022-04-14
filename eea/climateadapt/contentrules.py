# -*- coding: utf-8 -*-

from plone.api.portal import get_tool
import transaction
from OFS.SimpleItem import SimpleItem
#from plone.app.contentrules import PloneMessageFactory as _
from eea.climateadapt import CcaAdminMessageFactory as _
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.interface import Interface, implementer


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

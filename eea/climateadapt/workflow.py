""" Pages to deal with workflow
"""

from Products.CMFCore.interfaces import IContentish
from plone.api.content import transition
from plone.api.portal import show_message
from plone.autoform import directives
from plone.stringinterp.adapters import BaseSubstitution
from z3c.form import button, form     #, field
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.component.interfaces import ObjectEvent, IObjectEvent
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface


ANNOT_KEY = 'CCA_WORKFLOW_MESSAGE'


class IWorkflowMessageEvent(IObjectEvent):
    """ An event with a message for the workflow transition
    """

@implementer(IWorkflowMessageEvent)
class WorkflowMessageEvent(ObjectEvent):


class IWorkflowMessageSchema(Interface):
    """ Schema to set message on transition
    """

    directives.mode(workflow_action='hidden')
    workflow_action = schema.ASCIILine(title="Workflow action")
    message = schema.Text(title="Message", required=True)


class WorkflowTransitionMessage(form.Form):
    """ A form to trigger a workflow transition, together with workflow message

    How to use: set the URL for the workflow transition to something like:
    %(content_url)s/@@set_workflow_message?form.widgets.workflow_action=publish

    Use together with the "ClimateAdapt: workflow transition with message"
    content rule event type and the interpolation variable, ${workflow_message}
    """

    schema = IWorkflowMessageSchema
    ignoreContext = True

    label = "Send comment for this action"

    @property
    def description(self):
        action = self.request.get('form.widgets.workflow_action')
        return "This will trigger the {0} transition".format(action)

    def updateWidgets(self, prefix=None):
        super(WorkflowTransitionMessage, self).updateWidgets()
        v = self.request.get('form.widgets.workflow_action', None)
        if v:
            self.widgets['workflow_action'].value = v
        return

    @button.buttonAndHandler("Save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        action = data['workflow_action']
        msg = data['message'].strip()

        IAnnotations(self.request)[ANNOT_KEY] = msg
        notify(WorkflowMessageEvent(self.context))
        transition(obj=self.context, transition=action, comment=msg)

        self.status = msg = "Message will be further processed."
        show_message(message=msg, request=self.request, type='info')
        return self.request.response.redirect(self.context.absolute_url())


class workflow_message(BaseSubstitution):
    adapts(IContentish)

    category = 'CCA Utils'
    description = "Content of message set in workflow form."

    def safe_call(self):
        req = getRequest()
        return IAnnotations(req).get(ANNOT_KEY)

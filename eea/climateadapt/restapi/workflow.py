# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.interfaces._content import IWorkflowAware
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer

from eea.climateadapt.restapi.navigation import ICCARestapiLayer

import six


@implementer(IExpandableElement)
@adapter(IWorkflowAware, ICCARestapiLayer)
class WorkflowInfo(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "workflow": {"@id": "{}/@workflow".format(self.context.absolute_url())}
        }
        if not expand:
            return result

        # Prevent 404 on site root on workflow request
        # Although 404 will be more semantic, for the sake of uniformity of the
        # API we fake the response to the endpoint by providing an empty
        # response instead of a 404.
        if IPloneSiteRoot.providedBy(self.context):
            result["workflow"].update({"history": [], "transitions": []})
            return result

        wftool = getToolByName(self.context, "portal_workflow")
        try:
            history = wftool.getInfoFor(self.context, "review_history")
        except WorkflowException:
            history = []

        actions = wftool.listActionInfos(object=self.context)
        transitions = []
        for action in actions:
            if action["category"] != "workflow":
                continue

            title = action["title"]
            if isinstance(title, six.binary_type):
                title = title.decode("utf8")

            transitions.append(
                {
                    "@id": "{}/@workflow/{}".format(
                        self.context.absolute_url(), action["id"]
                    ),
                    "title": self.context.translate(title),
                }
            )

        for item, action in enumerate(history):
            title = wftool.getTitleForStateOnType(
                action["review_state"], self.context.portal_type
            )
            if isinstance(title, six.binary_type):
                title = title.decode("utf8")
            history[item]["title"] = self.context.translate(title)

        try:
            current_state = wftool.getInfoFor(self.context, "review_state")
        except WorkflowException:
            current_state = ""
        current_state_title = wftool.getTitleForStateOnType(
            current_state,
            self.context.portal_type,
        )

        result["workflow"].update(
            {
                "history": json_compatible(history),
                "transitions": transitions,
                "state": {
                    "id": current_state,
                    "title": self.context.translate(current_state_title),
                },
            }
        )
        return result


class WorkflowInfoService(Service):
    """Get workflow information"""

    def reply(self):
        info = WorkflowInfo(self.context, self.request)
        return info(expand=True)["workflow"]


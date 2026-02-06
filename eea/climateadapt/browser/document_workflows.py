from Products.Five.browser import BrowserView
from plone import api
from eea.climateadapt.scripts.document_workflows import get_workflow_data


class DocumentWorkflowsView(BrowserView):
    """A view to visualize workflow and content type associations."""

    def __call__(self):
        portal = api.portal.get()
        self.data = get_workflow_data(portal)
        return self.index()

from Products.Five.browser import BrowserView
from plone import api
from Products.CMFCore.utils import getToolByName


def get_workflow_data(portal):
    """Retrieve workflow data for all content types."""
    wftool = getToolByName(portal, "portal_workflow")
    ttool = getToolByName(portal, "portal_types")

    workflow_info = {}
    type_to_workflow = {}

    # Map content types to workflows
    for type_info in ttool.objectValues():
        type_id = type_info.getId()
        workflows = wftool.getChainForPortalType(type_id)
        type_to_workflow[type_id] = workflows

        for wf_id in workflows:
            if wf_id not in workflow_info:
                wf = wftool.getWorkflowById(wf_id)
                if not wf:
                    continue

                # We only support DCWorkflow for deep documentation
                if hasattr(wf, "states") and hasattr(wf, "transitions"):
                    managed_permissions = getattr(wf, "permissions", [])
                    states = {}
                    for state_id in wf.states.keys():
                        state = wf.states.get(state_id)
                        # Extract permission roles for this state
                        permissions = {}

                        # In DCWorkflow, permission_roles is a dict-like object
                        # mapping permission name to a tuple of roles.
                        raw_permissions = getattr(state, "permission_roles", {})

                        for perm in managed_permissions:
                            # Use the same logic DCWorkflow uses internally
                            roles = raw_permissions.get(perm, [])
                            if isinstance(roles, tuple):
                                roles = list(roles)
                            elif isinstance(roles, str):
                                roles = [roles]

                            permissions[perm] = roles

                        states[state_id] = {
                            "title": state.title or state_id,
                            "description": state.description,
                            "permissions": permissions,
                            "transitions": getattr(state, "transitions", []),
                        }

                    transitions = {}
                    for trans_id, trans in wf.transitions.items():
                        transitions[trans_id] = {
                            "title": trans.title or trans_id,
                            "new_state_id": trans.new_state_id,
                            "trigger": trans.trigger_type,
                        }

                    workflow_info[wf_id] = {
                        "title": wf.title or wf_id,
                        "initial_state": wf.initial_state,
                        "states": states,
                        "transitions": transitions,
                        "managed_permissions": managed_permissions,
                        "note": "",
                    }
                else:
                    workflow_info[wf_id] = {
                        "title": getattr(wf, "title", wf_id),
                        "initial_state": "unknown",
                        "states": {},
                        "transitions": {},
                        "managed_permissions": [],
                        "note": "Non-DCWorkflow type",
                    }

    return {
        "type_to_workflow": type_to_workflow,
        "workflow_definitions": workflow_info,
    }


class DocumentWorkflowsView(BrowserView):
    """A view to visualize workflow and content type associations."""

    def __call__(self):
        portal = api.portal.get()
        self.data = get_workflow_data(portal)
        return self.index()

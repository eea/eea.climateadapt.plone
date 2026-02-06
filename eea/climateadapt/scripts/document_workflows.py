"""Document workflows and content types"""

import argparse
import json
import logging
import sys

import Zope2
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import system as system_user
from Testing.makerequest import makerequest
from Zope2.Startup.run import make_wsgi_app
from zope.component.hooks import setSite
from zope.globalrequest import setRequest

from plone import api
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger(__name__)


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
                    for state_id, state in wf.states.items():
                        # Extract permission roles for this state
                        permissions = {}
                        if hasattr(state, "permission_roles"):
                            for perm in managed_permissions:
                                roles = state.getPermissionRoles(perm)
                                if isinstance(roles, str):
                                    # It might be a string if it's a single role
                                    roles = [roles]
                                permissions[perm] = roles

                        states[state_id] = {
                            "title": state.title or state_id,
                            "description": state.description,
                            "permissions": permissions,
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


def run(app):
    """Run the reporting logic."""
    parser = argparse.ArgumentParser(
        prog="DocumentWorkflows",
        description="Document content types and their associated workflows",
    )

    parser.add_argument(
        "--portal",
        dest="portal_id",
        required=True,
        help="Portal ID (e.g., cca)",
    )

    parser.add_argument(
        "--zope-conf",
        dest="zope_conf",
        required=True,
        help="Path to zope.conf",
    )

    parser.add_argument(
        "--json",
        dest="json_file",
        help="Path to JSON file to dump the report",
    )

    args = parser.parse_args()

    try:
        portal = app[args.portal_id]
    except KeyError:
        print(f"Error: Portal '{args.portal_id}' not found.")
        return

    setSite(portal)

    data = get_workflow_data(portal)

    if args.json_file:
        with open(args.json_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Report saved to {args.json_file}")
    else:
        print("Content Type to Workflow Mapping:")
        print("=" * 30)
        for type_id, workflows in sorted(data["type_to_workflow"].items()):
            wf_str = ", ".join(workflows) if workflows else "(no workflow)"
            print(f"{type_id}: {wf_str}")

        print("\nWorkflow Definitions:")
        print("=" * 30)
        for wf_id, info in sorted(data["workflow_definitions"].items()):
            print(f"\nWorkflow: {wf_id} ({info['title']})")
            print(f"  Initial State: {info['initial_state']}")
            
            print("  States:")
            for s_id, s_info in sorted(info["states"].items()):
                print(f"    - {s_id} ({s_info['title']})")
                if s_info.get("permissions"):
                    print("      Permissions:")
                    for perm, roles in sorted(s_info["permissions"].items()):
                        roles_str = ", ".join(roles) if roles else "(no roles)"
                        print(f"        {perm}: {roles_str}")

            print("  Transitions:")
            for t_id, t_info in sorted(info["transitions"].items()):
                target = t_info['new_state_id'] or "(remains in same state)"
                print(f"    - {t_id} ({t_info['title']}) -> {target}")


def main():
    # Use a minimal parser just to get zope_conf for bootstrapping
    bootstrap_parser = argparse.ArgumentParser(add_help=False)
    bootstrap_parser.add_argument("--zope-conf", dest="zope_conf", required=True)
    args, _ = bootstrap_parser.parse_known_args()

    make_wsgi_app({}, args.zope_conf)
    app = Zope2.app()
    app = makerequest(app)
    app.REQUEST["PARENTS"] = [app]
    setRequest(app.REQUEST)
    newSecurityManager(None, system_user)
    run(app)


if __name__ == "__main__":
    main()
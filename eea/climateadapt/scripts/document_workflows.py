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

from eea.climateadapt.browser.document_workflows import get_workflow_data


logger = logging.getLogger(__name__)


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
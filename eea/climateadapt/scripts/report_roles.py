"""Report roles"""

# trigger it with `docker compose exec backend /app/docker-entrypoint.sh bin/report_roles --portal cca --zope-conf etc/relstorage.conf`

import argparse
import csv
import logging

import Zope2
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import system as system_user
from Testing.makerequest import makerequest
from Zope2.Startup.run import make_wsgi_app

from zope.component.hooks import setSite
from zope.globalrequest import setRequest


logger = logging.getLogger(__name__)

IGNORED_USER_IDS = ["tibi", "tibiadmin", "tiberich", "admin", "zopeadmin"]

parser = argparse.ArgumentParser(
    prog="ReportRoles",
    description="Report local roles in the portal and subsites",
)

parser.add_argument(
    "--portal",
    dest="portal_id",
    required=True,
    help="Portal ID",
)

parser.add_argument(
    "--zope-conf",
    dest="zope_conf",
    required=True,
    help="Path to zope.conf",
)

parser.add_argument(
    "--csv",
    dest="csv_file",
    help="Path to CSV file to dump the report",
)

parser.add_argument(
    "--full",
    action="store_true",
    help="Include 'Owner' roles in the report (filtered by default)",
)


def get_roles_data(obj, path, include_owner=False):
    roles = obj.get_local_roles()
    filtered_roles = []

    for principal, role_list in roles:
        if principal in IGNORED_USER_IDS:
            continue

        if not include_owner:
            role_list = [r for r in role_list if r != "Owner"]

        if role_list:
            filtered_roles.append((principal, role_list))

    blocked = getattr(obj, "__ac_local_roles_block__", False)
    return {
        "path": path,
        "roles": filtered_roles,
        "blocked": bool(blocked),
    }


def run(app):
    """Run the reporting script."""
    args = parser.parse_args()

    try:
        portal = app[args.portal_id]
    except KeyError:
        print(f"Error: Portal '{args.portal_id}' not found.")
        return

    setSite(portal)

    # Initial paths to start recursion from
    start_paths = [
        "",  # portal root
        "en",
        "en/mission",
        "en/observatory",
    ]

    all_data = []
    seen_paths = set()

    def traverse(obj, current_rel_path):
        full_path = "/" + args.portal_id + (f"/{current_rel_path}" if current_rel_path else "")
        if full_path in seen_paths:
            return
        seen_paths.add(full_path)

        data = get_roles_data(obj, full_path, include_owner=args.full)
        # Include any object that has local roles or blocked inheritance
        if data["roles"] or data["blocked"]:
            all_data.append(data)

        # Recurse into children if it's folder-like
        if hasattr(obj, "objectValues"):
            for child in obj.objectValues():
                id = child.getId()
                # Skip some obviously uninteresting system folders/objects if they appear
                if id in ["portal_catalog", "portal_workflow", "portal_types"]:
                    continue

                # For Climate-ADAPT, we want to skip the translation folders during recursion
                # if they are at the root level (e.g., /cca/ro, /cca/de)
                # except for 'en' which is our starting point anyway.
                if not current_rel_path and id in [
                    "bg", "cs", "da", "de", "el", "es", "et", "fi", "fr", "ga",
                    "hr", "hu", "it", "lt", "lv", "mt", "nl", "pl", "pt", "ro",
                    "sk", "sl", "sv"
                ]:
                    continue

                child_rel_path = (f"{current_rel_path}/{id}" if current_rel_path else id)
                traverse(child, child_rel_path)

    for rel_path in start_paths:
        try:
            if not rel_path:
                obj = portal
            else:
                obj = portal.unrestrictedTraverse(rel_path)
            traverse(obj, rel_path)
        except Exception as e:
            print(f"\nCould not access path '{rel_path}': {e}")

    if args.csv_file:
        with open(args.csv_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Path", "Principal", "Roles", "Inheritance Blocked"])
            for entry in all_data:
                path = entry["path"]
                blocked = entry["blocked"]
                if not entry["roles"]:
                    writer.writerow([path, "(no local roles)", "", blocked])
                for principal, role_list in entry["roles"]:
                    writer.writerow([path, principal, ", ".join(role_list), blocked])
        print(f"\nReport saved to: {args.csv_file}")
    else:
        for entry in all_data:
            print(f"\nLocal roles for: {entry['path']}")
            if entry["blocked"]:
                print("  [Inheritance BLOCKED]")

            if not entry["roles"]:
                print("  (no local roles)")
                continue

            for principal, role_list in entry["roles"]:
                print(f"  {principal}: {', '.join(role_list)}")


def main():
    args = parser.parse_args()
    make_wsgi_app({}, args.zope_conf)
    app = Zope2.app()
    app = makerequest(app)
    app.REQUEST["PARENTS"] = [app]
    setRequest(app.REQUEST)
    newSecurityManager(None, system_user)
    run(app)


if __name__ == "__main__":
    main()

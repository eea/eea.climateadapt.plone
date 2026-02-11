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

from eea.climateadapt.local_roles import get_local_roles_report


logger = logging.getLogger(__name__)


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


def run(app):
    """Run the reporting script."""
    args = parser.parse_args()

    try:
        portal = app[args.portal_id]
    except KeyError:
        print(f"Error: Portal '{args.portal_id}' not found.")
        return

    setSite(portal)

    all_data = get_local_roles_report(portal, include_owner=args.full)

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

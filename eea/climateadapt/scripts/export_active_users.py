"""Export IDs of users who have created or modified objects in the last N years.

This script traverses the ``/en`` content tree to find users active in a
given lookback period. It checks each content object's ``created`` and
``modified`` dates and collects the associated user IDs.

Only the canonical English folder is scanned; translation folders are
excluded since they are auto-synced.

Two metrics are tracked per user:

1. **Created** — number of objects where the user is the ``creator`` and
   the object's ``created`` date falls within the lookback period.

2. **Modified** — number of objects whose ``modified`` date falls within
   the lookback period, attributed to the object's ``creator``.
   Note: Plone does not track ``modified_by`` by default, so this
   captures the original author of objects that were recently modified,
   not necessarily the user who performed the last edit.

The script supports console output, CSV export, and JSON export.

Example::

    docker compose exec backend /app/docker-entrypoint.sh \\
        bin/export_active_users --portal cca --zope-conf etc/relstorage.conf

    # CSV export
    docker compose exec backend /app/docker-entrypoint.sh \\
        bin/export_active_users --portal cca --zope-conf etc/relstorage.conf \\
        --csv active_users.csv

    # JSON export, 3-year window
    docker compose exec backend /app/docker-entrypoint.sh \\
        bin/export_active_users --portal cca --zope-conf etc/relstorage.conf \\
        --json active_users.json --years 3
"""

import argparse
import csv
import json
import logging
import sys
from collections import Counter
from datetime import datetime, timedelta

from DateTime import DateTime

import Zope2
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import system as system_user
from Testing.makerequest import makerequest
from Zope2.Startup.run import make_wsgi_app
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
from zope.interface import implementer
from OFS.interfaces import IFolder
from plone.dexterity.interfaces import IDexterityContent

logger = logging.getLogger(__name__)


def traverse_content(portal):
    """Stack-based traversal of Dexterity content under /en.

    Only the canonical English folder is traversed; translation folders
    (/ro, /de, etc.) are skipped. Yields (path, object) tuples.
    System tools and non-content objects are skipped.
    """
    en_folder = portal.get("en")
    if en_folder is None:
        logger.error("Portal has no 'en' folder — nothing to traverse.")
        return

    stack = [("/en", en_folder)]
    while stack:
        path, container = stack.pop()
        try:
            for id in container.objectIds():
                try:
                    obj = container[id]
                except Exception:
                    continue

                obj_path = f"{path}/{id}"

                if IDexterityContent.providedBy(obj):
                    yield obj_path, obj

                if IFolder.providedBy(obj):
                    stack.append((obj_path, obj))
        except Exception as e:
            logger.warning("Error traversing %s: %s", path, e)


def collect_active_users(portal, since):
    """Traverse all content and collect creator/modifier counts.

    Args:
        portal: The Plone portal object.
        since: datetime — only count activity from this date onwards.

    Returns:
        (creators, modifiers) — two Counter objects mapping user_id -> count.
    """
    creators = Counter()
    modifiers = Counter()
    scanned = 0
    errors = 0

    for path, obj in traverse_content(portal):
        scanned += 1
        try:
            # Check created date + creator
            try:
                created = obj.created()
                if created and created >= since:
                    creator = obj.Creator()
                    if creator:
                        creators[creator] += 1
            except Exception:
                pass

            # Check modified date + author
            try:
                modified = obj.modified()
                if modified and modified >= since:
                    # Prefer author, fall back to creator
                    author = obj.Creator()
                    if author:
                        modifiers[author] += 1
            except Exception:
                pass

        except Exception as e:
            errors += 1
            if errors <= 10:
                logger.warning("Error processing %s: %s", path, e)

    logger.info("Scanned %d objects (%d errors)", scanned, errors)
    return creators, modifiers


def run(portal, years=2, csv_file=None, json_file=None):
    """Main logic: traverse content and produce output."""
    since = DateTime(datetime.now() - timedelta(days=years * 365))
    logger.info("Looking back %d years (since %s)", years, since)

    print(
        f"Scanning for active users (last {years} years, since {since.strftime('%Y-%m-%d')})..."
    )
    # DateTime.strftime works the same as datetime.strftime
    print()

    creators, modifiers = collect_active_users(portal, since)

    # Merge: union of all user IDs
    all_users = sorted(set(creators.keys()) | set(modifiers.keys()))

    results = [
        {
            "user_id": uid,
            "objects_created": creators.get(uid, 0),
            "objects_modified": modifiers.get(uid, 0),
        }
        for uid in all_users
    ]

    # Console output (always)
    print(f"{'User ID':<40} {'Created':>10} {'Modified':>10}")
    print("-" * 62)
    for entry in results:
        print(
            f"{entry['user_id']:<40} {entry['objects_created']:>10} {entry['objects_modified']:>10}"
        )
    print("-" * 62)
    print(f"Total active users: {len(results)}")
    print(f"  Created objects:  {sum(e['objects_created'] for e in results)}")
    print(f"  Modified objects: {sum(e['objects_modified'] for e in results)}")

    # CSV output
    if csv_file:
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["user_id", "objects_created", "objects_modified"]
            )
            writer.writeheader()
            writer.writerows(results)
        print(f"CSV saved to {csv_file} ({len(results)} users)")

    # JSON output
    if json_file:
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"JSON saved to {json_file} ({len(results)} users)")


def main():
    parser = argparse.ArgumentParser(
        prog="ExportActiveUsers",
        description="Export IDs of users who have created or modified objects in the last N years.",
    )
    parser.add_argument(
        "--portal", dest="portal_id", required=True, help="Portal ID (e.g., cca)"
    )
    parser.add_argument(
        "--zope-conf", dest="zope_conf", required=True, help="Path to zope.conf"
    )
    parser.add_argument(
        "--csv", dest="csv_file", help="Path to CSV file to dump the report"
    )
    parser.add_argument(
        "--json", dest="json_file", help="Path to JSON file to dump the report"
    )
    parser.add_argument(
        "--years",
        type=int,
        default=2,
        help="Lookback period in years (default: 2)",
    )

    # Bootstrap Zope
    make_wsgi_app({}, parser.parse_args().zope_conf)
    app = Zope2.app()
    app = makerequest(app)
    app.REQUEST["PARENTS"] = [app]
    setRequest(app.REQUEST)
    newSecurityManager(None, system_user)

    args = parser.parse_args()

    try:
        portal = app[args.portal_id]
    except KeyError:
        print(f"Error: Portal '{args.portal_id}' not found.")
        sys.exit(1)

    setSite(portal)
    run(portal, years=args.years, csv_file=args.csv_file, json_file=args.json_file)


if __name__ == "__main__":
    main()

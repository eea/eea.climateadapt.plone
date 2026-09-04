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
from Products.CMFCore.utils import getToolByName

from eea.climateadapt.local_roles import IGNORED_USER_IDS
from eea.climateadapt.scripts.export_eionet_groups import (
    connect,
    fetch_groups,
    fetch_users,
    find_ldap_settings,
    member_uid,
)

logger = logging.getLogger(__name__)

# Developer/staff accounts that show up in content changes but are not real
# portal users; excluded from the report (same list as report_roles).
DEVELOPER_USER_IDS = {uid.lower() for uid in IGNORED_USER_IDS}

DEFAULT_LDAP_EXCLUDE_FILTER = "extranet-cca*"


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


def get_user_details(portal, user_ids):
    """Resolve user IDs to fullname/email via portal_membership.

    Returns: dict user_id -> {"fullname": str, "email": str}
    """
    portal_membership = getToolByName(portal, "portal_membership")
    details = {}
    for uid in user_ids:
        try:
            member = portal_membership.getMemberById(uid)
            if member is None:
                details[uid] = {"fullname": "", "email": ""}
                continue
            details[uid] = {
                "fullname": (member.getProperty("fullname") or "").strip(),
                "email": (member.getProperty("email") or "").strip(),
            }
        except Exception as e:
            logger.warning("Could not fetch member details for %s: %s", uid, e)
            details[uid] = {"fullname": "", "email": ""}
    return details


def get_ldap_group_members(portal, cn_filter):
    """Fetch the set of Eionet usernames that are members of the LDAP groups
    matching ``cn_filter`` (e.g. ``extranet-cca*``).

    Requires the EEA VPN to be connected. Raises on connection failure.
    """
    settings = find_ldap_settings(portal.acl_users)
    con = connect(settings)
    try:
        groups = fetch_groups(con, settings, cn_filter)
    finally:
        con.unbind()
    uids = set()
    for group in groups:
        for member_dn in group["members"]:
            uid = member_uid(member_dn)
            if uid:
                uids.add(uid)
    return uids


def run(portal, years=2, csv_file=None, json_file=None, no_ldap=False,
        ldap_exclude_filter=DEFAULT_LDAP_EXCLUDE_FILTER):
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
    all_users = set(creators.keys()) | set(modifiers.keys())

    # Drop developer/staff accounts (see IGNORED_USER_IDS in local_roles.py)
    dev_users = {uid for uid in all_users if uid.lower() in DEVELOPER_USER_IDS}
    if dev_users:
        print(f"Ignoring developer/staff accounts: {', '.join(sorted(dev_users))}")
        print()
        all_users -= dev_users

    # Exclude users that are members of the Eionet LDAP groups, and fetch
    # LDAP user details to fill missing local fullname/email.
    excluded_users = set()
    ldap_details = {}
    if no_ldap:
        print(f"LDAP lookup skipped (--no-ldap).")
        print()
    else:
        print(
            f"Fetching LDAP groups (cn={ldap_exclude_filter}) and user details..."
        )
        try:
            settings = find_ldap_settings(portal.acl_users)
            con = connect(settings)
            try:
                groups = fetch_groups(con, settings, ldap_exclude_filter)
                for group in groups:
                    for member_dn in group["members"]:
                        uid = member_uid(member_dn)
                        if uid:
                            # member_uid() already lowercases
                            excluded_users.add(uid)
                # fetch_users() keys results by lowercased uid
                ldap_details = fetch_users(con, settings, [f"uid={u}" for u in all_users])
            finally:
                con.unbind()
        except Exception as e:
            print(
                f"Warning: could not fetch from LDAP ({e}).\n"
                "Make sure the EEA VPN is connected, or re-run with --no-ldap "
                "to skip the LDAP lookup."
            )
            print()
        else:
            print(
                f"  {len(excluded_users)} users are members of those LDAP groups; "
                f"{len(ldap_details)} users found in the LDAP directory."
            )
            print()

    details = get_user_details(portal, all_users)
    # Fill missing local details from LDAP (case-insensitive uid match)
    for uid in all_users:
        ldap_info = ldap_details.get(uid.lower())
        if ldap_info:
            if not details[uid]["fullname"]:
                details[uid]["fullname"] = ldap_info["fullname"]
            if not details[uid]["email"]:
                details[uid]["email"] = ldap_info["email"]
    results = []
    excluded_results = []
    for uid in sorted(all_users):
        entry = {
            "user_id": uid,
            "fullname": details[uid]["fullname"],
            "email": details[uid]["email"],
            "objects_created": creators.get(uid, 0),
            "objects_modified": modifiers.get(uid, 0),
        }
        if uid.lower() in excluded_users:
            excluded_results.append(entry)
        else:
            results.append(entry)

    fieldnames = [
        "user_id",
        "fullname",
        "email",
        "objects_created",
        "objects_modified",
    ]

    def print_table(entries):
        print(f"{'User ID':<16} {'Full name':<30} {'Email':<35} {'Created':>8} {'Modified':>8}")
        print("-" * 101)
        for entry in entries:
            print(
                f"{entry['user_id']:<16} {entry['fullname']:<30} {entry['email']:<35} "
                f"{entry['objects_created']:>8} {entry['objects_modified']:>8}"
            )
        print("-" * 101)

    # Console output (always)
    print_table(results)
    print(f"Total active users: {len(results)}")
    print(f"  Created objects:  {sum(e['objects_created'] for e in results)}")
    print(f"  Modified objects: {sum(e['objects_modified'] for e in results)}")
    if excluded_results:
        print()
        print(f"Excluded (member of LDAP groups matching {ldap_exclude_filter}): {len(excluded_results)}")
        print_table(excluded_results)

    # CSV output
    if csv_file:
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
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
    parser.add_argument(
        "--no-ldap",
        action="store_true",
        help=(
            "Skip fetching Eionet LDAP groups (also skips the group-member "
            "exclusion). Use when the EEA VPN is not connected."
        ),
    )
    parser.add_argument(
        "--ldap-exclude-filter",
        dest="ldap_exclude_filter",
        default=DEFAULT_LDAP_EXCLUDE_FILTER,
        help=(
            "LDAP wildcard filter for groups whose members are excluded "
            f"(default: {DEFAULT_LDAP_EXCLUDE_FILTER})"
        ),
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
    run(
        portal,
        years=args.years,
        csv_file=args.csv_file,
        json_file=args.json_file,
        no_ldap=args.no_ldap,
        ldap_exclude_filter=args.ldap_exclude_filter,
    )


if __name__ == "__main__":
    main()

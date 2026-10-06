"""Map EntraID users from Eionet LDAP group memberships to local Plone groups.

Queries Eionet LDAP group memberships (or reads a CSV exported by
export_eionet_groups.py), finds corresponding EntraID users in Plone (by matching
email addresses), and adds them to the respective local groups
(e.g., extranet-cca-editors -> local-cca-editors).

See MAP_ENTRAID_TO_LOCAL_GROUPS.md for documentation.
"""

import argparse
import csv
import logging
import sys
from collections import defaultdict

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog="MapEntraIDToLocalGroups",
    description=(
        "Map EntraID users from Eionet LDAP group memberships to local Plone groups. "
        "Supports direct LDAP lookup (requires EEA VPN) or pre-exported CSV input."
    ),
)

parser.add_argument(
    "--portal",
    dest="portal_id",
    default="cca",
    help="Portal ID (default: cca)",
)

parser.add_argument(
    "--zope-conf",
    dest="zope_conf",
    required=True,
    help="Path to zope.conf or relstorage.conf",
)

parser.add_argument(
    "--run",
    action="store_true",
    help="Commit changes to the database (default: dry-run mode)",
)

parser.add_argument(
    "--eionet-csv",
    dest="eionet_csv",
    help=(
        "Path to CSV exported by export_eionet_groups.py. "
        "If omitted, connects directly to Eionet LDAP."
    ),
)

parser.add_argument(
    "--filter",
    dest="cn_filter",
    default="extranet-cca*",
    help="LDAP wildcard filter for groups when querying LDAP directly (default: extranet-cca*)",
)

parser.add_argument(
    "--group",
    dest="target_group_filter",
    help="Limit processing to a specific LDAP group name (e.g. extranet-cca-editors)",
)

parser.add_argument(
    "--prefix-from",
    dest="prefix_from",
    default="extranet-",
    help="Prefix in LDAP group name to replace (default: extranet-)",
)

parser.add_argument(
    "--prefix-to",
    dest="prefix_to",
    default="local-",
    help="Prefix for target local group name (default: local-)",
)

parser.add_argument(
    "--csv",
    dest="output_csv",
    help="Path to CSV file to export detailed mapping results",
)

parser.add_argument(
    "--verbose",
    action="store_true",
    help="Enable verbose output",
)


def map_group_name(ldap_group, prefix_from="extranet-", prefix_to="local-"):
    """Map an LDAP group name to its local Plone group counterpart."""
    if prefix_from and ldap_group.startswith(prefix_from):
        return ldap_group.replace(prefix_from, prefix_to, 1)
    if prefix_to and not ldap_group.startswith(prefix_to):
        return f"{prefix_to}{ldap_group}"
    return ldap_group


def load_memberships_from_csv(csv_path):
    """Load group memberships from a CSV exported by export_eionet_groups.py."""
    memberships = []
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            group = (row.get("group") or row.get("Group") or "").strip()
            if not group:
                continue
            memberships.append(
                {
                    "group": group,
                    "username": (row.get("username") or row.get("uid") or "").strip(),
                    "fullname": (row.get("fullname") or row.get("cn") or "").strip(),
                    "email": (row.get("email") or row.get("mail") or "").strip(),
                    "member_dn": (row.get("member_dn") or "").strip(),
                }
            )
    return memberships


def load_memberships_from_ldap(portal, cn_filter):
    """Query Eionet LDAP directly for group memberships using pasldap settings."""
    from eea.climateadapt.scripts.export_eionet_groups import (
        find_ldap_settings,
        connect,
        fetch_groups,
        fetch_users,
        member_uid,
    )

    acl_users = portal.acl_users
    settings = find_ldap_settings(acl_users)
    try:
        con = connect(settings)
    except Exception as exc:
        raise RuntimeError(
            f"Could not connect to Eionet LDAP server ({settings.get('server.uri')}): {exc}\n"
            "Make sure the EEA VPN is connected, or provide a pre-exported CSV using --eionet-csv <file.csv>."
        )

    try:
        groups = fetch_groups(con, settings, cn_filter)
        all_members = set()
        for g in groups:
            all_members.update(g["members"])
        users = fetch_users(con, settings, all_members)
    finally:
        con.unbind()

    memberships = []
    for g in groups:
        for member_dn in g["members"]:
            uid = member_uid(member_dn)
            info = users.get(uid, {})
            memberships.append(
                {
                    "group": g["cn"],
                    "username": uid,
                    "fullname": info.get("fullname", ""),
                    "email": info.get("email", ""),
                    "member_dn": member_dn,
                }
            )
    return memberships


def build_plone_user_index(portal):
    """Build an in-memory email -> user mapping from Plone PAS plugins.

    Scans:
      1. authomatic plugin: _useridentities_by_userid (primary EntraID store)
      2. mutable_properties plugin: _storage
    """
    index = {}
    acl_users = getattr(portal, "acl_users", None)
    if not acl_users:
        return index

    # 1. authomatic plugin (stores EntraID identities keyed by plone_uuid)
    authomatic = getattr(acl_users, "authomatic", None)
    if authomatic and hasattr(authomatic, "_useridentities_by_userid"):
        for plone_uuid, uis in authomatic._useridentities_by_userid.items():
            sheet = getattr(uis, "propertysheet", None) or getattr(uis, "_sheet", None)
            if not sheet:
                continue
            fullname = sheet.getProperty("fullname", "") or sheet.getProperty("displayName", "")
            for prop in ("email", "mail", "userPrincipalName"):
                email_val = sheet.getProperty(prop, "")
                if email_val and isinstance(email_val, str) and "@" in email_val:
                    em_clean = email_val.strip().lower()
                    if em_clean not in index:
                        index[em_clean] = {
                            "user_id": str(plone_uuid),
                            "login": sheet.getProperty("email", str(plone_uuid)),
                            "fullname": fullname,
                            "email": email_val.strip(),
                            "source": "authomatic",
                        }

    # 2. mutable_properties storage
    mutable_props = getattr(acl_users, "mutable_properties", None)
    if mutable_props and hasattr(mutable_props, "_storage"):
        for user_id, sheet in mutable_props._storage.items():
            fullname = ""
            email_val = ""
            if hasattr(sheet, "getProperty"):
                fullname = sheet.getProperty("fullname", "")
                email_val = sheet.getProperty("email", "")
            elif isinstance(sheet, dict):
                fullname = sheet.get("fullname", "")
                email_val = sheet.get("email", "")
            if email_val and isinstance(email_val, str) and "@" in email_val:
                em_clean = email_val.strip().lower()
                if em_clean not in index:
                    index[em_clean] = {
                        "user_id": str(user_id),
                        "login": str(user_id),
                        "fullname": fullname,
                        "email": email_val.strip(),
                        "source": "mutable_properties",
                    }

    return index


def find_user_in_plone(portal, email, index=None):
    """Look up an existing user in Plone by email address (case-insensitive)."""
    if not email:
        return None

    email_clean = email.strip()
    em_lower = email_clean.lower()

    if index and em_lower in index:
        return index[em_lower]

    acl_users = getattr(portal, "acl_users", None)
    if not acl_users:
        return None

    # Search by login (authomatic / eea_entra uses email as login)
    try:
        users = acl_users.searchUsers(login=email_clean, exact_match=True)
        if users:
            u = users[0]
            res = {
                "user_id": u.get("id") or u.get("userid"),
                "login": u.get("login") or u.get("id"),
                "fullname": u.get("title") or u.get("fullname", ""),
                "email": email_clean,
                "source": "acl_users (login)",
            }
            if index is not None:
                index[em_lower] = res
            return res
    except Exception:
        pass

    # Search by email property
    try:
        users = acl_users.searchUsers(email=email_clean, exact_match=True)
        if users:
            u = users[0]
            res = {
                "user_id": u.get("id") or u.get("userid"),
                "login": u.get("login") or u.get("id"),
                "fullname": u.get("title") or u.get("fullname", ""),
                "email": email_clean,
                "source": "acl_users (email)",
            }
            if index is not None:
                index[em_lower] = res
            return res
    except Exception:
        pass

    # portal_membership fallback
    try:
        from Products.CMFCore.utils import getToolByName
        mtool = getToolByName(portal, "portal_membership", None)
    except ImportError:
        mtool = getattr(portal, "portal_membership", None)
    if mtool:
        try:
            member = mtool.getMemberById(email_clean)
            if member:
                res = {
                    "user_id": member.getId(),
                    "login": member.getUserName(),
                    "fullname": member.getProperty("fullname", ""),
                    "email": member.getProperty("email", email_clean),
                    "source": "portal_membership (id)",
                }
                if index is not None:
                    index[em_lower] = res
                return res
        except Exception:
            pass

    return None


def run(app, args):
    """Execute the EntraID to local groups mapping."""
    import transaction
    from zope.component.hooks import setSite
    from Products.CMFCore.utils import getToolByName

    try:
        portal = app[args.portal_id]
    except KeyError:
        print(f"Error: Portal '{args.portal_id}' not found.")
        return

    setSite(portal)
    dry_run = not args.run
    portal_groups = getToolByName(portal, "portal_groups")

    mode_str = "DRY-RUN (use --run to commit changes)" if dry_run else "LIVE RUN (changes will be committed)"
    print(f"\n{'=' * 80}")
    print(f"Mapping EntraID Users to Local Groups [{mode_str}]")
    print(f"Portal: {args.portal_id}")
    print(f"{'=' * 80}")

    # 1. Load memberships
    if args.eionet_csv:
        print(f"Loading Eionet LDAP memberships from CSV: {args.eionet_csv}")
        memberships = load_memberships_from_csv(args.eionet_csv)
    else:
        print(f"Querying live Eionet LDAP (filter: cn={args.cn_filter})...")
        try:
            memberships = load_memberships_from_ldap(portal, args.cn_filter)
        except Exception as exc:
            print(f"Error loading LDAP memberships: {exc}")
            return

    if args.target_group_filter:
        memberships = [m for m in memberships if m["group"] == args.target_group_filter]
        print(f"Filtered to target LDAP group '{args.target_group_filter}': {len(memberships)} rows")
    else:
        print(f"Total LDAP membership rows to process: {len(memberships)}")

    # 2. Build Plone user index
    print("Indexing known Plone/EntraID users in acl_users...")
    user_index = build_plone_user_index(portal)
    print(f"  Indexed {len(user_index)} user email(s) across authomatic / mutable_properties.")

    # 3. Group memberships by LDAP group
    by_ldap_group = defaultdict(list)
    for m in memberships:
        by_ldap_group[m["group"]].append(m)

    # 4. Process each group
    results = []
    stats = {
        "groups_seen": 0,
        "groups_created": 0,
        "already_member": 0,
        "added": 0,
        "would_add": 0,
        "user_not_found": 0,
        "no_email": 0,
    }

    for ldap_group, group_memberships in sorted(by_ldap_group.items()):
        stats["groups_seen"] += 1
        local_group = map_group_name(ldap_group, args.prefix_from, args.prefix_to)

        print(f"\nGroup: {ldap_group} -> {local_group}")
        print(f"  LDAP members: {len(group_memberships)}")

        # Ensure local group exists
        target_group_obj = portal_groups.getGroupById(local_group)
        if not target_group_obj:
            if not dry_run:
                print(f"  [+] Creating local group: {local_group}")
                portal_groups.addGroup(
                    local_group,
                    title=local_group,
                    description=f"Migrated from LDAP {ldap_group}",
                )
                target_group_obj = portal_groups.getGroupById(local_group)
                stats["groups_created"] += 1
            else:
                print(f"  [*] Would create local group: {local_group}")
                stats["groups_created"] += 1

        existing_member_ids = set()
        if target_group_obj:
            try:
                existing_member_ids = set(target_group_obj.getMemberIds())
            except Exception:
                try:
                    existing_member_ids = set(portal_groups.getGroupMembers(local_group))
                except Exception:
                    pass

        for m in group_memberships:
            username = m["username"]
            fullname = m["fullname"]
            email = m["email"]

            if not email:
                stats["no_email"] += 1
                status = "NO_EMAIL"
                notes = "User has no email in LDAP; cannot match to EntraID"
                if args.verbose:
                    print(f"    [-] {username:<16} {fullname:<30} [NO EMAIL]")
                results.append({
                    "ldap_group": ldap_group,
                    "local_group": local_group,
                    "ldap_username": username,
                    "ldap_fullname": fullname,
                    "email": "",
                    "plone_user_id": "",
                    "plone_fullname": "",
                    "status": status,
                    "notes": notes,
                })
                continue

            # Look up EntraID user in Plone
            user_info = find_user_in_plone(portal, email, user_index)
            if not user_info:
                stats["user_not_found"] += 1
                status = "USER_NOT_FOUND"
                notes = "Not found in Plone (user has not logged in via EntraID or not synced)"
                if args.verbose:
                    print(f"    [?] {username:<16} {fullname:<30} {email:<35} [NOT IN PLONE]")
                results.append({
                    "ldap_group": ldap_group,
                    "local_group": local_group,
                    "ldap_username": username,
                    "ldap_fullname": fullname,
                    "email": email,
                    "plone_user_id": "",
                    "plone_fullname": "",
                    "status": status,
                    "notes": notes,
                })
                continue

            plone_uid = user_info["user_id"]
            plone_fn = user_info["fullname"] or fullname

            if plone_uid in existing_member_ids:
                stats["already_member"] += 1
                status = "ALREADY_MEMBER"
                notes = f"Already in {local_group}"
                if args.verbose:
                    print(f"    [=] {username:<16} {plone_fn:<30} {email:<35} [ALREADY MEMBER]")
            else:
                if not dry_run:
                    portal_groups.addPrincipalToGroup(plone_uid, local_group)
                    existing_member_ids.add(plone_uid)
                    stats["added"] += 1
                    status = "ADDED"
                    notes = f"Added to {local_group}"
                    print(f"    [+] ADDED: {username} ({email}) -> {local_group} [uid={plone_uid}]")
                else:
                    stats["would_add"] += 1
                    status = "WOULD_ADD"
                    notes = f"Would add to {local_group}"
                    print(f"    [*] WOULD ADD: {username} ({email}) -> {local_group} [uid={plone_uid}]")

            results.append({
                "ldap_group": ldap_group,
                "local_group": local_group,
                "ldap_username": username,
                "ldap_fullname": fullname,
                "email": email,
                "plone_user_id": plone_uid,
                "plone_fullname": plone_fn,
                "status": status,
                "notes": notes,
            })

    # 5. Commit if live run
    if not dry_run:
        print("\nCommitting changes to database...")
        transaction.commit()
        print("Changes committed successfully.")
    else:
        print("\nDry-run completed. No changes committed to the database.")

    # 6. Summary
    print(f"\n{'=' * 80}")
    print("Summary:")
    print(f"  Groups processed:           {stats['groups_seen']}")
    print(f"  Groups created/would create: {stats['groups_created']}")
    print(f"  Total memberships checked:  {len(memberships)}")
    if dry_run:
        print(f"  Users to add (WOULD_ADD):   {stats['would_add']}")
    else:
        print(f"  Users added (ADDED):        {stats['added']}")
    print(f"  Already members:            {stats['already_member']}")
    print(f"  Users not found in Plone:   {stats['user_not_found']} (need EntraID login or sync_eea_entra)")
    print(f"  Members with missing email: {stats['no_email']}")
    print(f"{'=' * 80}")

    # 7. CSV Export
    if args.output_csv:
        fieldnames = [
            "ldap_group",
            "local_group",
            "ldap_username",
            "ldap_fullname",
            "email",
            "plone_user_id",
            "plone_fullname",
            "status",
            "notes",
        ]
        with open(args.output_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nDetailed report saved to: {args.output_csv}")


def main():
    args = parser.parse_args()
    import Zope2
    from AccessControl.SecurityManagement import newSecurityManager
    from AccessControl.users import system as system_user
    from Testing.makerequest import makerequest
    from Zope2.Startup.run import make_wsgi_app
    from zope.globalrequest import setRequest

    make_wsgi_app({}, args.zope_conf)
    app = Zope2.app()
    app = makerequest(app)
    app.REQUEST["PARENTS"] = [app]
    setRequest(app.REQUEST)
    newSecurityManager(None, system_user)
    run(app, args)


if __name__ == "__main__":
    main()

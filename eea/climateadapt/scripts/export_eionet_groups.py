"""Export Eionet LDAP group memberships.

Queries the Eionet LDAP directory (using the connection settings of the
``pasldap`` PAS plugin configured in the site's ``acl_users``) for groups
matching a ``cn`` filter (default ``extranet-cca*``) and prints/exports the
members of each group with their Eionet username, full name and email.

NOTE: The LDAP server is only reachable from inside the EEA network. Make
sure the EEA VPN is connected before running this script.

See EXPORT_EIONET_GROUPS.md for documentation.
"""

import argparse
import csv
import logging

import ldap
import Zope2
from ldap import ldapobject
from Zope2.Startup.run import make_wsgi_app

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog="ExportEionetGroups",
    description=(
        "Export memberships of Eionet LDAP groups (default: extranet-cca*). "
        "Requires the EEA VPN to be connected."
    ),
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
    "--filter",
    dest="cn_filter",
    default="extranet-cca*",
    help=(
        "LDAP wildcard filter applied to the group cn attribute "
        "(default: extranet-cca*)"
    ),
)

parser.add_argument(
    "--csv",
    dest="csv_file",
    help="Path to CSV file to dump the membership report",
)


def _txt(value):
    """Decode bytes to str defensively (search results may mix both)."""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def find_ldap_settings(acl_users):
    """Find the PAS LDAP plugin and return its settings tree."""
    for plugin in acl_users.objectValues():
        settings = getattr(plugin, "settings", None)
        if settings is None:
            continue
        try:
            uri = settings["server.uri"]
        except (KeyError, TypeError):
            continue
        if "ldap" in _txt(uri).lower():
            logger.info("Using LDAP plugin: %s", plugin.id)
            return settings
    raise RuntimeError(
        "No PAS LDAP plugin with server settings found in acl_users. "
        "Check the plugins of %s/acl_users." % acl_users.getId()
    )


def connect(settings):
    """Open an LDAP connection using the plugin's own recipe.

    Replicates node.ext.ldap.base (used by pas.plugins.ldap): a plain
    connection without OPT_X_TLS_NEVER fails the TLS handshake.
    """
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    con = ldapobject.ReconnectLDAPObject(
        settings["server.uri"],
        bytes_mode=False,
        bytes_strictness="silent",
        retry_max=1,
        retry_delay=1,
    )
    con.set_option(ldap.OPT_REFERRALS, 0)
    con.protocol_version = ldap.VERSION3
    conn_timeout = settings.get("server.conn_timeout")
    if conn_timeout:
        con.set_option(ldap.OPT_NETWORK_TIMEOUT, int(conn_timeout))
    con.simple_bind_s(settings["server.user"], settings["server.password"])
    logger.info("Bound to %s as %s", settings["server.uri"], settings["server.user"])
    return con


def fetch_groups(con, settings, cn_filter):
    """Fetch groups matching the cn filter. -> list of dicts."""
    base = _txt(settings["groups.baseDN"])
    flt = "(&(objectClass=hierarchicalGroup)(cn=%s))" % cn_filter
    res = con.search_s(base, 2, flt, ["cn", "description", "member", "uniqueMember"])
    groups = []
    for dn, attrs in res:
        if not dn:
            continue
        cn = _txt((attrs.get("cn") or ["?"])[0])
        desc = _txt((attrs.get("description") or [""])[0])
        members = [_txt(m) for m in (attrs.get("member") or [])]
        members += [_txt(m) for m in (attrs.get("uniqueMember") or [])]
        # Legacy entries can contain empty member values
        members = [m for m in members if m.strip()]
        groups.append({"cn": cn, "dn": _txt(dn), "description": desc, "members": members})
    groups.sort(key=lambda g: g["cn"])
    return groups


def fetch_users(con, settings, member_dns):
    """Resolve user DNs to (uid, cn, mail). -> dict uid -> {fullname, email}"""
    uids = set()
    for dn in member_dns:
        if dn.lower().startswith("uid="):
            uids.add(dn.split(",", 1)[0][4:].lower())
    users = {}
    base = _txt(settings["users.baseDN"])
    chunk = 40
    uid_list = sorted(uids)
    for i in range(0, len(uid_list), chunk):
        flt = "(|%(uids)s)" % {
            "uids": "".join("(uid=%s)" % u for u in uid_list[i : i + chunk])
        }
        res = con.search_s(base, 2, flt, ["uid", "cn", "mail"])
        for dn, attrs in res:
            if not dn:
                continue
            uid = _txt((attrs.get("uid") or ["?"])[0]).lower()
            users[uid] = {
                "fullname": _txt((attrs.get("cn") or [""])[0]),
                "email": _txt((attrs.get("mail") or [""])[0]),
            }
    return users


def member_uid(member_dn):
    """Extract the uid from a user DN (empty string for non-user DNs)."""
    if member_dn.lower().startswith("uid="):
        return member_dn.split(",", 1)[0][4:].lower()
    return ""


def run(app):
    """Run the export."""
    args = parser.parse_args()

    try:
        portal = app[args.portal_id]
    except KeyError:
        print(f"Error: Portal '{args.portal_id}' not found.")
        return

    acl_users = portal.acl_users
    settings = find_ldap_settings(acl_users)

    try:
        con = connect(settings)
    except Exception as exc:
        print(
            "Error: could not connect to the LDAP server "
            f"({settings['server.uri']}): {exc}\n"
            "Make sure the EEA VPN is connected."
        )
        return

    try:
        groups = fetch_groups(con, settings, args.cn_filter)
        print(
            f"Found {len(groups)} groups matching cn={args.cn_filter} "
            f"under {_txt(settings['groups.baseDN'])}"
        )

        all_members = set()
        for group in groups:
            all_members.update(group["members"])
        users = fetch_users(con, settings, all_members)
    finally:
        con.unbind()

    rows = []
    for group in groups:
        print(
            f"\n{group['cn']}  ({group['dn']})"
            + (f"  — {group['description']}" if group["description"] else "")
        )
        member_rows = []
        for member_dn in group["members"]:
            uid = member_uid(member_dn)
            info = users.get(uid, {})
            member_rows.append(
                {
                    "group": group["cn"],
                    "username": uid,
                    "fullname": info.get("fullname", ""),
                    "email": info.get("email", ""),
                    "member_dn": member_dn,
                }
            )
        member_rows.sort(key=lambda r: (not r["username"], r["username"]))
        rows.extend(member_rows)
        print(f"  members: {len(member_rows)}")
        for row in member_rows:
            if row["username"]:
                print(
                    f"    {row['username']:<16} {row['fullname']:<35} "
                    f"{row['email']}"
                )
            else:
                print(f"    (non-user entry: {row['member_dn']})")

    unique_users = {
        row["username"]: row for row in rows if row["username"]
    }
    print(f"\nTotal group rows: {len(rows)}")
    print(f"Unique users across all groups: {len(unique_users)}")
    unresolved = len(all_members) - len({m for m in all_members if member_uid(m) in users})
    if unresolved:
        print(f"Warning: {unresolved} member DN(s) could not be resolved to users.")

    if args.csv_file:
        with open(args.csv_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["group", "username", "fullname", "email", "member_dn"],
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nReport saved to: {args.csv_file}")


def main():
    args = parser.parse_args()
    make_wsgi_app({}, args.zope_conf)
    app = Zope2.app()
    run(app)


if __name__ == "__main__":
    main()

# Export Eionet Groups Script

This script exports the **memberships of Eionet LDAP groups** by querying the
Eionet LDAP directory directly, using the connection settings of the `pasldap`
PAS plugin configured in the site's `acl_users` (server URI, bind DN/password,
base DNs). For each group it reports every member with their Eionet username
(`uid`), full name (`cn`) and email (`mail`), resolved from the LDAP users
tree.

## Rationale

Climate-ADAPT is moving from Eionet LDAP authentication to Microsoft Entra ID
(see `docs/entraid.md`). Before LDAP is retired, this script provides the
authoritative list of which Eionet users belong to each `extranet-cca-*`
group — the raw material for deciding who needs their account/permissions
remapped to the new authentication system.

Companion scripts:

- `migrate_eionet_groups` — migrates `extranet-*` → `local-*` **local role** references inside Plone
- `report_roles` — reports local role assignments **in Plone** (per content path)
- `export_active_users` — exports users active in Plone content

This script is the only one that reads the **LDAP directory itself** (groups and
users that may have no local Plone profile).

## Features

- **Reuses the plugin's connection settings** — no credentials are stored in
  the script; they are read at runtime from `acl_users.pasldap.settings`.
- **Configurable group filter** — defaults to `cn=extranet-cca*`; any LDAP
  wildcard filter on the group `cn` works (e.g. `*mission*`).
- **User detail resolution** — member DNs are resolved in batched queries to
  the users base DN, yielding username, full name and email.
- **Console + CSV output** — a readable per-group table on stdout, plus an
  optional flat CSV (one row per group membership).
- **Non-user member entries** (e.g. nested group DNs) are reported as-is
  instead of being silently dropped.

## Prerequisites

- **EEA VPN must be connected.** The LDAP server (`ldap.eionet.europa.eu:636`)
  is not reachable from outside the EEA network; without the VPN the script
  exits with a connection error.
- The site's `acl_users` must contain a PAS LDAP plugin with `server.*`
  settings (the `pasldap` plugin in the `cca` portal).

## How to Run

### Using Makefile (Recommended)

From the `backend/` directory:

```bash
# Console report (default filter: extranet-cca*)
make export-eionet-groups

# CSV export to backend/eionet_groups.csv
make export-eionet-groups-csv

# Different group filter
make export-eionet-groups ARGS="--filter '*mission*'"
```

### Manual Execution

```bash
docker compose exec backend /app/docker-entrypoint.sh /app/bin/python3 \
    /app/sources/eea.climateadapt/eea/climateadapt/scripts/export_eionet_groups.py \
    --portal cca --zope-conf etc/relstorage.conf
```

> The Makefile targets invoke the script from the mounted source tree
> (`/app/sources/...`) so no package reinstall is needed. The `bin/export_eionet_groups`
> console script becomes available after a normal package reinstall.

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--portal` | yes | — | Portal ID (usually `cca`) |
| `--zope-conf` | yes | — | Path to zope configuration file |
| `--filter` | no | `extranet-cca*` | LDAP wildcard filter applied to the group `cn` attribute |
| `--csv` | no | — | Path to CSV output file |

## Output

### Console

```
Found 14 groups matching cn=extranet-cca* under ou=Roles,o=EIONET,l=Europe

extranet-cca-checkers  (cn=extranet-cca-checkers,cn=extranet-cca,cn=extranet,ou=Roles,o=EIONET,l=Europe)  — Content checkers - view pending content, no editing.
  members: 5
    user1            Example User                  user1@example.com
    ...

Total group rows: 126
Unique users across all groups: 78
```

### CSV

```csv
group,username,fullname,email,member_dn
extranet-cca-checkers,user1,Example User,user1@example.com,uid=user1,ou=Users,o=EIONET,l=Europe
```

One row per group membership, so users in multiple groups appear multiple
times. `username` is empty for non-user member entries (see `member_dn`).

## Implementation Details

- **Connection**: Replicates the `node.ext.ldap` recipe used by
  `pas.plugins.ldap` — `ReconnectLDAPObject` with
  `ldap.OPT_X_TLS_REQUIRE_CERT = OPT_X_TLS_NEVER` (honoring the plugin's
  `ignore_cert` setting), referrals off, protocol v3, network timeout from
  `server.conn_timeout`. A plain `LDAPObject` without the TLS option fails the
  handshake on this OpenSSL-based python-ldap build.
- **Group search**: base DN from `groups.baseDN`, subtree scope, filter
  `(&(objectClass=hierarchicalGroup)(cn=<filter>))`.
- **User resolution**: all member DNs starting with `uid=` are collected,
  then resolved in batches of 40 with `(|(uid=...)(uid=...))` searches against
  `users.baseDN`, keeping LDAP round-trips low.
- **Bytes handling**: search results may contain `bytes` values even with
  `bytes_strictness='silent'`; all values are decoded defensively.

## Limitations

- **Direct membership only** — a user is listed for a group only if they are a
  direct `member`/`uniqueMember` of that group entry. Users reachable only via
  nested subgroups (e.g. a user of `-ma-managers` is *also* listed under
  `-ma` only if Eionet maintains that redundancy) may not appear in the parent.
  The `extranet-cca` parent group appears to hold the union of all members, so
  cross-check against it.
- **Read-only** — the script only performs LDAP searches; it never modifies
  the directory or the Plone database.
- **VPN-dependent** — cannot be used for CI/automation outside the EEA network.
- **User attributes** — only `uid`, `cn`, `mail` are fetched; other
  attributes (e.g. `l` location) are available in the users tree if needed.

## Troubleshooting

- **"could not connect to the LDAP server"**: VPN not connected (or split-tunnel
  not covering `87.54.7.x`). Verify with
  `docker compose exec backend sh -c 'timeout 8 bash -c "cat < /dev/null > /dev/tcp/ldap.eionet.europa.eu/636" && echo OPEN'`.
- **"No PAS LDAP plugin ... found in acl_users"**: the portal's `acl_users`
  has no plugin exposing `settings['server.uri']` — check the plugin
  configuration (expected plugin ID: `pasldap`).
- **`ldap.INVALID_CREDENTIALS`**: the plugin's bind DN/password no longer
  work against the LDAP server; update the `pasldap` plugin settings.
- **Users with empty fullname/email**: the user DN exists in a group but has
  no matching `uid` under the users base DN (or lacks `cn`/`mail`
  attributes); check the `member_dn` column in the CSV.

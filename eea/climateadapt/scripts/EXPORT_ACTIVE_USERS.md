# Export Active Users Script

This script exports the IDs of users who have been active in the portal within a configurable lookback period (default: 2 years). Activity is measured by objects **created** or **modified** by/for those users. Each user is reported with their **full name** and **email** (from the local `portal_membership` profiles) so they can be identified.

Only the canonical English (`/en`) folder is scanned; translation folders (`/ro`, `/de`, etc.) are excluded since they are auto-synced.

## Rationale

Useful for auditing which users are still active, cleaning up inactive accounts, or understanding content authorship patterns over time.

In the context of the Eionet LDAP → Microsoft Entra ID migration (see `docs/entraid.md`), the LDAP group exclusion is the key feature: users who already belong to an `extranet-cca-*` LDAP group will be carried over with their group membership, so they are excluded from the export. What remains is the list of users who are active in the portal but **not** covered by any CCA LDAP group — the ones that need individual attention (account remapping, group assignment, or deactivation) during the migration.

## Features

- **Two-pass catalog query**: Separately identifies creators and modifiers.
- **User details**: Full name and email resolved from `portal_membership`, with missing values filled in from the LDAP users tree (LDAP-only users who never logged in locally have no local profile).
- **LDAP group exclusion**: By default, users who are members of any `extranet-cca-*` Eionet LDAP group (queried live, see `EXPORT_EIONET_GROUPS.md`) are excluded from the report. Excluded users are still listed on the console for transparency. Requires the EEA VPN; use `--no-ldap` to skip.
- **Developer account exclusion**: Developer/staff accounts from `IGNORED_USER_IDS` (`eea/climateadapt/local_roles.py`, the same list used by `report_roles`) are dropped from the report entirely; they are listed on the console when present.
- **Configurable lookback**: Default 2 years, adjustable via `--years`.
- **Multiple output formats**: Console table, CSV, or JSON.
- **Efficient batched queries**: Uses `batch_size` to avoid loading all results into memory at once.

## How to Run

### Using Makefile (Recommended)

From the `backend/` directory:

```bash
# Console report (last 2 years)
make export-active-users

# Console report (last 3 years)
make export-active-users ARGS="--years 3"

# CSV export
make export-active-users-csv

# JSON export
make export-active-users-json
```

### Manual Execution

```bash
docker compose exec backend /app/docker-entrypoint.sh \
    bin/export_active_users --portal cca --zope-conf etc/relstorage.conf

# Without LDAP exclusion (no EEA VPN available)
docker compose exec backend /app/docker-entrypoint.sh \
    bin/export_active_users --portal cca --zope-conf etc/relstorage.conf --no-ldap
```

> The console `bin/export_active_users` becomes available after a package
> reinstall. Until then, run the script directly from the mounted source tree:
> `/app/sources/eea.climateadapt/eea/climateadapt/scripts/export_active_users.py`.

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--portal` | yes | — | Portal ID (usually `cca`) |
| `--zope-conf` | yes | — | Path to zope configuration file |
| `--csv` | no | — | Path to CSV output file |
| `--json` | no | — | Path to JSON output file |
| `--years` | no | `2` | Lookback period in years |
| `--no-ldap` | no | off | Skip the LDAP group fetch and the group-member exclusion |
| `--ldap-exclude-filter` | no | `extranet-cca*` | LDAP wildcard filter for groups whose members are excluded |

## Output Formats

### Console

```
Scanning for active users (last 2 years, since 2023-06-15)...

Fetching LDAP group members matching cn=extranet-cca*...
  45 users are members of those LDAP groups.

User ID            Full name                      Email                             Created Modified
-------------------------------------------------------------------------------------------------
admin              Administrator                  admin@localhost                      150      200
contributor1       Jane Contributor               jane@example.com                       5        3
-------------------------------------------------------------------------------------------------
Total active users: 2
  Created objects:  155
  Modified objects: 203

Excluded (member of LDAP groups matching extranet-cca*): 1

User ID            Full name                      Email                             Created Modified
-------------------------------------------------------------------------------------------------
editor1            John Editor                    john@example.com                     45       80
-------------------------------------------------------------------------------------------------
```

### CSV

```csv
user_id,fullname,email,objects_created,objects_modified
admin,Administrator,admin@localhost,150,200
contributor1,Jane Contributor,jane@example.com,5,3
```

### JSON

```json
[
  {"user_id": "admin", "fullname": "Administrator", "email": "admin@localhost", "objects_created": 150, "objects_modified": 200},
  {"user_id": "contributor1", "fullname": "Jane Contributor", "email": "jane@example.com", "objects_created": 5, "objects_modified": 3}
]
```

> CSV/JSON contain **only the non-excluded users**; excluded users appear on the console only.

## Implementation Details

- **User details**: Resolved via `portal_membership.getMemberById(uid)` → `fullname`/`email` properties; empty values are then filled from the LDAP users tree (`fetch_users` from `export_eionet_groups.py`, matched case-insensitively on `uid`). Local values win when present.
- **Developer accounts**: `IGNORED_USER_IDS` from `eea.climateadapt.local_roles` (lowercased) is subtracted from the user set before the LDAP lookup and report; matches `report_roles` behavior.
- **LDAP exclusion**: Reuses the connection helpers of `export_eionet_groups.py` (`find_ldap_settings`, `connect`, `fetch_groups`, `member_uid`); collects the union of all `uid=` member DNs of the matching LDAP groups and removes those usernames from the report. If the LDAP connection fails (e.g. no VPN), the script warns and continues with **no** exclusion.
- **Tree traversal**: Walks the content tree under `/en` using a stack-based approach (no recursion). Each object's `created()`/`modified()` dates and `Creator()` are checked directly.
- **English only**: Only the canonical `/en` folder is traversed. Translation folders (`/ro`, `/de`, etc.) are excluded.
- **Scalability**: On a ~12k object `/en` tree, traversal takes ~4 seconds. The stack-based approach avoids `RecursionError` on deep structures.
- **Error resilience**: Each object is wrapped in `try/except` so a single broken object doesn't abort the scan.

## Limitations

### No `modified_by` tracking

Plone does not track which user last modified an object. The "Modified" column attributes recently-modified objects to their original `Creator()`, not the person who performed the last edit.

### English content only

Only `/en` is scanned. If you need to include other language folders, modify the `traverse_content` function to add additional starting folders.

### System users included

The script does not filter out system accounts (e.g., `Anonymous`, `system`). If you want to exclude these, filter the CSV/JSON output downstream.

### LDAP exclusion depends on VPN and the live directory

The exclusion list reflects the LDAP groups at run time and only contains users whose DNs start with `uid=`. Without the EEA VPN the exclusion is skipped with a warning (the script does not fail).

## Troubleshooting

- **"Portal not found"**: Ensure the `--portal` argument matches the actual portal ID in your ZODB (usually `cca` for Climate-ADAPT).
- **"Portal has no 'en' folder"**: The portal structure doesn't have an `/en` folder. Check the portal root's `objectIds()` to find the correct starting point.
- **Slow execution**: On a ~12k object `/en` tree, traversal takes ~4 seconds. If the tree is much larger, consider increasing the lookback period filter or running during off-peak hours.

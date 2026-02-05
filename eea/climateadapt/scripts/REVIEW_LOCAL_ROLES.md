# Local Roles Reporting Script

This script is a Zope command-line utility designed to report local role grants across the Climate-ADAPT portal and its main subsites.

## Rationale

Climate-ADAPT is a multilingual site. However, only the canonical English (`/en`) folder and its specific subsites are manually edited for roles. Translation folders (e.g., `/ro`, `/de`) are automatically synced and thus excluded from this report to keep the output focused on the source of truth for authority and permissions.

## Features

- Reports local roles for the **Portal Root**.
- Reports local roles for the **Main Site** (`/en`).
- Reports local roles for the **Mission Subsite** (`/en/mission`).
- Reports local roles for the **Observatory Subsite** (`/en/observatory`).
- Detects and flags **Inheritance Blocking** (where `__ac_local_roles_block__` is set).

## How to Run

The script is registered as a console script within the `eea.climateadapt` package and is available in the backend container's `bin/` directory.

To run the report, use the following command from the `backend` folder (where `docker-compose.yml` is located):

```bash
docker compose exec backend /app/docker-entrypoint.sh bin/report_roles --portal cca --zope-conf etc/relstorage.conf
```

To generate a CSV report:

```bash
docker compose exec backend /app/docker-entrypoint.sh bin/report_roles --portal cca --zope-conf etc/relstorage.conf --csv roles_report.csv
```

### Arguments

- `--portal`: The ID of the Plone portal (usually `cca`).
- `--zope-conf`: Path to the Zope configuration file (usually `etc/relstorage.conf` in this environment).
- `--csv`: (Optional) Path to a CSV file to dump the report.
- `--full`: (Optional) Include 'Owner' roles in the report. By default, entries that only have 'Owner' roles (and no blocked inheritance) are hidden to reduce noise.

## Output Format

The script prints the path being inspected, followed by a list of principals and their assigned roles. If inheritance is blocked at that level, it is explicitly indicated.

Example output:
```text
Local roles for: /cca
  [Inheritance BLOCKED]
  admin: Manager
  EditorGroup: Editor, Reviewer

Local roles for: /cca/en
  principal_id: Role1, Role2
```

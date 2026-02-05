# Local Roles Reporting Script

This script is a Zope command-line utility designed to report local role grants across the Climate-ADAPT portal and its main subsites.

## Rationale

Climate-ADAPT is a multilingual site. However, only the canonical English (`/en`) folder and its specific subsites are manually edited for roles. Translation folders (e.g., `/ro`, `/de`) are automatically synced and thus excluded from this report to keep the output focused on the source of truth for authority and permissions.

## Features

- **Recursive Reporting**: Automatically traverses the portal root and key subsites (`/en`, `/en/mission`, `/en/observatory`) to find nested local roles.
- **Noise Reduction**: 
    - Filters out "uninteresting" users (e.g., developers like `tibi`, `tiberich`, and system admins).
    - By default, hides entries that only have the `Owner` role assigned (unless inheritance is blocked at that level).
- **Inheritance Detection**: Flags objects where inheritance is explicitly blocked (`__ac_local_roles_block__`).
- **Multiple Output Formats**: Supports both human-readable console output and machine-readable CSV export.

## How to Run

The script is available via Makefile shortcuts or directly via `docker compose exec`.

### Using Makefile (Recommended)

From the project root (where `Makefile` is located):

```bash
# Standard console report
make report-roles

# Generate CSV report (saved as roles_report.csv in the container)
make report-roles-csv

# Include 'Owner' roles in the report
make report-roles ARGS="--full"
```

### Manual Execution

```bash
docker compose exec backend /app/docker-entrypoint.sh bin/report_roles --portal cca --zope-conf etc/relstorage.conf
```

To generate a CSV report:

```bash
docker compose exec backend /app/docker-entrypoint.sh bin/report_roles --portal cca --zope-conf etc/relstorage.conf --csv roles_report.csv
```

## Arguments

- `--portal`: The ID of the Plone portal (usually `cca`).
- `--zope-conf`: Path to the Zope configuration file (usually `etc/relstorage.conf`).
- `--csv`: (Optional) Path to a CSV file to dump the report.
- `--full`: (Optional) Include 'Owner' roles in the report. By default, entries that only have 'Owner' roles (and no blocked inheritance) are hidden to reduce noise.

## Implementation Details

- **Traversal**: The script uses `objectValues()` to recursively explore all folderish content.
- **Excluded Paths**: Root-level translation folders (e.g., `/cca/ro`, `/cca/bg`) are automatically skipped during recursion.
- **Ignored Users**: The `IGNORED_USER_IDS` constant in `report_roles.py` defines which principals are excluded from the report.

## Output Format

The script prints the path being inspected, followed by a list of principals and their assigned roles.

Example output:
```text
Local roles for: /cca/en/mission
  [Inheritance BLOCKED]
  AuthenticatedUsers: Reader
  extranet-cca-mission: Contributor, Reviewer, Editor, Reader
  yilmabek: Manager
```
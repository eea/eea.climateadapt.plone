# Local Roles Reporting Script

This script is a Zope command-line utility designed to report local role grants across the Climate-ADAPT portal and its main subsites.

## Rationale

Climate-ADAPT is a multilingual site. However, only the canonical English (`/en`) folder and its specific subsites are manually edited for roles. Translation folders (e.g., `/ro`, `/de`) are automatically synced and thus excluded from this report to keep the output focused on the source of truth for authority and permissions.

## Features

- **Iterative Reporting**: Automatically traverses the portal root and key subsites (`/en`, `/en/mission`, `/en/observatory`) using a stack-based approach for maximum robustness.
- **Noise Reduction**: 
    - Filters out "uninteresting" users (e.g., developers like `tibi`, `tiberich`, and system admins).
    - By default, hides entries that only have the `Owner` role assigned (unless inheritance is blocked at that level).
- **Inheritance Detection**: Flags objects where inheritance is explicitly blocked (`__ac_local_roles_block__`).
- **Multiple Output Formats**: Supports both human-readable console output and machine-readable CSV export.
- **Fault Tolerance**: Designed to continue the report even if specific objects or folders encounter errors during traversal.

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

- **Traversal**: The script uses a stack-based **iterative traversal** (instead of recursion) to explore content. This avoids `RecursionError` on deep structures and allows the script to recover from errors within specific branches.
- **Content Filtering**: Instead of brittle hardcoded "skip lists" for system tools, it uses Zope interfaces (`IDexterityContent`, `IPloneSiteRoot`) to identify valid content.
- **Dynamic Exclusion**: Root-level translation folders (e.g., `/cca/ro`, `/cca/bg`) are dynamically identified using the `ILanguageRootFolder` interface and skipped.
- **Error Resilience**: Each object and its children are processed within `try...except` blocks. If an object is corrupted or a path is inaccessible, the script logs the error and continues with the rest of the database.

### Lessons Learnt

1. **Avoid Recursion for DB Crawls**: In large Zope databases, recursion can be dangerous. An unhandled exception or a `RecursionError` in one branch (like a deep translation folder) can abort the entire reporting process, masking data in other branches.
2. **Interface over IDs**: Checking for `IDexterityContent` is more maintainable than maintaining a list of system IDs (`portal_catalog`, `portal_workflow`, etc.) to skip.
3. **Partial Failures are Better than Total Failures**: When crawling a complex CMS, always wrap the "work" per object in a try-except. This ensures that a single problematic object doesn't prevent the user from seeing the rest of the report.

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
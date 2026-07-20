# Export Active Users Script

This script exports the IDs of users who have been active in the portal within a configurable lookback period (default: 2 years). Activity is measured by objects **created** or **modified** by/for those users.

Only the canonical English (`/en`) folder is scanned; translation folders (`/ro`, `/de`, etc.) are excluded since they are auto-synced.

## Rationale

Useful for auditing which users are still active, cleaning up inactive accounts, or understanding content authorship patterns over time.

## Features

- **Two-pass catalog query**: Separately identifies creators and modifiers.
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
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--portal` | yes | — | Portal ID (usually `cca`) |
| `--zope-conf` | yes | — | Path to zope configuration file |
| `--csv` | no | — | Path to CSV output file |
| `--json` | no | — | Path to JSON output file |
| `--years` | no | `2` | Lookback period in years |

## Output Formats

### Console

```
Scanning for active users (last 2 years, since 2023-06-15)...

User ID                                   Created   Modified
--------------------------------------------------------------
admin                                         150        200
editor1                                        45         80
contributor1                                    5          3
--------------------------------------------------------------
Total active users: 3
  Created objects:  200
  Modified objects: 283
```

### CSV

```csv
user_id,objects_created,objects_modified
admin,150,200
editor1,45,80
contributor1,5,3
```

### JSON

```json
[
  {"user_id": "admin", "objects_created": 150, "objects_modified": 200},
  {"user_id": "editor1", "objects_created": 45, "objects_modified": 80},
  {"user_id": "contributor1", "objects_created": 5, "objects_modified": 3}
]
```

## Implementation Details

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

## Troubleshooting

- **"Portal not found"**: Ensure the `--portal` argument matches the actual portal ID in your ZODB (usually `cca` for Climate-ADAPT).
- **"Portal has no 'en' folder"**: The portal structure doesn't have an `/en` folder. Check the portal root's `objectIds()` to find the correct starting point.
- **Slow execution**: On a ~12k object `/en` tree, traversal takes ~4 seconds. If the tree is much larger, consider increasing the lookback period filter or running during off-peak hours.

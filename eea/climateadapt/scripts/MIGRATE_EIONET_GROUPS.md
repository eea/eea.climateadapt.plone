# Migrate Eionet Groups Script

This script is a Zope command-line utility designed to migrate local role assignments from old LDAP-based groups (prefixed with `extranet-`) to new local Plone groups (prefixed with `local-`).

## Rationale

Climate-ADAPT is moving away from direct LDAP group mapping for local roles in favor of local Plone groups. This script ensures that any existing local role assignments for `extranet-*` groups are replicated to corresponding `local-*` groups, ensuring a smooth transition.

## Features

- **Full Database Traversal**: Unlike the reporting script, this script crawls the entire portal including all language folders to ensure no local role assignments are missed.
- **Automatic Group Creation**: If a `local-*` group does not exist for a corresponding `extranet-*` group found in local roles, it is automatically created.
- **Idempotency**: The script can be run multiple times. If a `local-*` group already has the same roles as the `extranet-*` group on an object, it won't be duplicated.
- **Dry-run Mode**: Enabled by default, allowing you to see what changes would be made without actually modifying the database.
- **Iterative Traversal**: Uses a stack-based approach for robustness and to avoid recursion depth issues.

## How to Run

The script is executed using the `docker compose exec backend /app/docker-entrypoint.sh` command.

### Dry-run (Safe)

```bash
docker compose exec backend /app/docker-entrypoint.sh bin/migrate_eionet_groups --portal cca --zope-conf etc/relstorage.conf
```

### Actual Migration

```bash
docker compose exec backend /app/docker-entrypoint.sh bin/migrate_eionet_groups --portal cca --zope-conf etc/relstorage.conf --run
```

## Arguments

- `--portal`: The ID of the Plone portal (usually `cca`).
- `--zope-conf`: Path to the Zope configuration file (usually `etc/relstorage.conf`).
- `--run`: (Optional) If provided, the script will commit changes to the database. Without this flag, it runs in dry-run mode.

## Implementation Details

- **Group Prefix**: It looks for principals starting with `extranet-` and maps them to `local-`.
- **Plone Groups**: It uses `portal_groups` to create the new groups if they don't exist.
- **Transaction Management**: When running in non-dry-run mode, it commits the transaction at the end.

# Console Scripts

Built-in scripts in `eea/climateadapt/scripts/` that can be run against the live database using the inline execution pattern described in [agent-debugging.md](./agent-debugging.md).

## Scripts that connect to the live database

These scripts bootstrap the full Zope/Plone application (RelStorage → PostgreSQL):

| Script | Purpose |
|--------|---------|
| [report_roles.py](../eea/climateadapt/scripts/report_roles.py) | Reports all local roles defined in the portal and subsites. |
| [analyze_relstorage.py](../eea/climateadapt/scripts/analyze_relstorage.py) | Analyzes raw RelStorage object counts and sizes by iterating transactions/records. Opens RelStorage directly (does not need full Plone bootstrap). |
| [migrate_eionet_groups.py](../eea/climateadapt/scripts/migrate_eionet_groups.py) | Crawls all content and migrates `extranet-*` groups → `local-*` groups in local roles. Supports `--run` flag to commit changes. |
| [document_workflows.py](../eea/climateadapt/scripts/document_workflows.py) | Documents content type → workflow mappings (read-only). |
| [c3s.py](../eea/climateadapt/scripts/c3s.py) | Fetches C3S indicator data from a remote URL and creates/updates content objects. |
| [harvest_eea_indicators.py](../eea/climateadapt/scripts/harvest_eea_indicators.py) | Queries an EEA SPARQL endpoint and triggers Plone content rules. |
| [sync_to_arcgis.py](../eea/climateadapt/scripts/sync_to_arcgis.py) | Reads Plone config for RabbitMQ, then consumes messages and processes content. |

## Scripts that do NOT connect to the database

These operate on exported JSON files or external APIs only:

| Script | Purpose |
|--------|---------|
| [fix_content.py](../eea/climateadapt/scripts/fix_content.py) | Processes exported JSON files on disk (content fixers for migration). |
| [list_broken_content.py](../eea/climateadapt/scripts/list_broken_content.py) | Processes exported JSON files on disk (finds invalid field values). |
| [fix_localroles.py](../eea/climateadapt/scripts/fix_localroles.py) | Filters localroles keys from an exported JSON file. |
| [cli_arcgis_client.py](../eea/climateadapt/scripts/cli_arcgis_client.py) | CLI for ArcGIS REST API operations (HTTP only). |
| [_debug.py](../eea/climateadapt/scripts/_debug.py) | Debugging helpers for ArcGIS API (HTTP requests only). |

## Running a script

Run from the `backend/` directory:

```bash
cat sources/eea.climateadapt/eea/climateadapt/scripts/report_roles.py | \
  docker compose exec -T backend /app/docker-entrypoint.sh /app/bin/python3 - \
  --portal cca \
  --zope-conf /app/etc/relstorage.conf
```

See [agent-debugging.md](./agent-debugging.md) for the full inline execution pattern.

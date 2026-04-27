# RelStorage Analysis Script

This script is a Zope command-line utility designed to analyze the distribution of objects within the RelStorage database, providing statistics on counts and sizes per Python class.

## Rationale

The ZODB can grow significantly over time, and identifying which objects contribute most to its size is essential for database maintenance and optimization. While `zodb analyze` exists, this script is tailored for RelStorage environments and provides a direct way to scan the SQL-backed storage to identify large or numerous objects by class.

## Features

- **Deep Scan**: Iterates through all transactions and records in the RelStorage database.
- **Class-Level Reporting**: Groups objects by their full Python class name (module + class).
- **Size Analysis**: Reports total size (in MB) and average size (in Bytes) for each class.
- **Bypass App**: Connects directly to the database storage, allowing it to run without loading the full Plone application environment (bypassing `Zope2.app()`).

## How to Run

The script is registered as a console script and should be run within the Docker environment.

### Setup

Ensure that the package dependencies are installed within the container to register the entry points:

```bash
docker compose exec backend bin/pip install -r requirements-mxdev.txt
```

### Execution

Run the script using `docker compose exec`. You must provide the path to the Zope or RelStorage configuration file.

```bash
docker compose exec backend /app/docker-entrypoint.sh bin/analyze_relstorage --zope-conf etc/relstorage.conf
```

## Implementation Details

- **Direct Storage Access**: Uses `Zope2.Startup.options.ZopeWSGIOptions` to parse the database configuration. This ensures that environment variables and conditional imports (like `tempstorage`) are handled correctly, consistent with how Zope itself starts.
- **Metadata Extraction**: Utilizes `ZODB.utils.get_pickle_metadata` to extract class information from pickled data without fully unpickling the objects, which is significantly faster and safer.
- **Transaction Iteration**: Uses the `iterator()` method of the storage to traverse the database history.

## Output Format (Console Example)

```text
Scanning RelStorage... this will take a moment.

CLASS                                                        | COUNT      | TSIZE (MB) | AVG SIZE (B)
----------------------------------------------------------------------------------------------------
plone.app.contenttypes.content.Document                      | 15000      | 45.20      | 3160
btrees.OOBTree.OOBucket                                      | 42000      | 12.50      | 312
eea.climateadapt.content.ClimateAdaptContent                 | 5000       | 8.10       | 1700
...
```

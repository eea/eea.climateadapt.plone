# Import Extended Tools Script

This script is a command-line utility and web-view backend for importing and updating **Extended Tools** (`eea.climateadapt.extendedtool`) into Climate-ADAPT from OpenDocument Spreadsheet (`.ods`) and CSV files.

It populates the content items used by the Navigator Tools Catalogue and the Volto frontend (`volto-cca-policy`'s `ExtendedToolView`).

---

## Rationale & Background

The Climate-ADAPT tools catalogue data was provided in two separate `.ods` spreadsheets:

1. **File 1 — Main metadata**:
   `v2-20+26_newDB_input_from_factsheets+information_from_Tool_Database.ods`
   Contains core metadata for 46 tools: title, short description, external ID, sectors, climate impacts, geographic coverage/scope, spatial resolution, user requirements, intended user groups, data types, accessibility, etc.
2. **File 2 — Rich text descriptions & use cases**:
   `Tools_extra_fields_tool_page EDWxlsx.ods`
   Contains the detailed qualitative fields for 57 tools:
   - **Use it to** (`use_it_to`) — bullet points of practical use cases
   - **Inputs** (`tool_input`) — bullet points of data/input requirements
   - **Outputs** (`tool_output`) — bullet points of tool outputs/visualizations
   - **Why it's relevant to climate adaptation** (`climate_adaptation_relevance`) — explanatory paragraph
   - **Used in / Already applied to** (`used_in`) — bullet points of real-world applications

Merging both datasets produces **59 unique tools** (43 in both, 3 unique to File 1, 14 unique to File 2).

The importer parses both files directly, joins them by tool ID (e.g. `#10`), formats bullets into clean HTML lists (`<ul><li>...</li></ul>`), and creates or updates `eea.climateadapt.extendedtool` objects under `/cca/en/metadata/tools`.

---

## Architecture & Shared Implementation

To prevent code duplication, the importer logic is centralized in:

- **Core Module**: `eea.climateadapt.scripts.import_extended_tools`
  - `ExtendedToolsImporter`: Handles row parsing, header resolution, taxonomy normalization, dataset merging, and Plone object population.
  - `parse_ods_rows()`: Direct OpenDocument XML parser using Python's standard library (`zipfile` + `xml.etree.ElementTree`). Properly handles multi-row bullet continuations resulting from vertically merged cells (`table:covered-table-cell`).
- **CLI Entrypoint**: `import_extended_tools = eea.climateadapt.scripts.import_extended_tools:main`
- **Browser View**: `ToolExtendFields` in `eea.climateadapt.browser.migrate` (registered at `@@tool_extendfields_372446`), delegating directly to `ExtendedToolsImporter.run_web_import()`.

---

## Features

- **Safe Dry-Run by Default**: When run from the command line without `--commit`, it validates all data, parses both spreadsheets, and reports exactly what would be created or updated without writing to the ZODB.
- **In-Place Updates & Idempotence**: Finds existing items by `external_id` (e.g. `#10`) or matching title. Running the script multiple times updates existing objects without creating duplicate records.
- **Container Constrain Management**: Automatically ensures `eea.climateadapt.extendedtool` is enabled in `ISelectableConstrainTypes` on `/cca/en/metadata/tools`.
- **Clean Rich Text Formatting**: Strips legacy bullet artifacts (`•`, `-`, extra spaces) and wraps bullet lists in proper `<ul><li>...</li></ul>` and paragraphs in `<p>...</p>` using `plone.app.textfield.value.RichTextValue`.
- **Batch Savepoints & Catalog Indexing**: Creates transaction savepoints periodically during import and triggers catalog reindexing for each item.

---

## How to Run

### 1. From Command Line (Docker Environment)

Data files can be placed in `backend/sources/eea.climateadapt/data/` (which mounts inside the container at `/app/sources/eea.climateadapt/data/`).

> **Note**: Always invoke via `/app/docker-entrypoint.sh` so that environment variables required by ZConfig/RelStorage are properly loaded.

#### Dry-Run (Preview only):

```bash
docker compose -f backend/docker-compose.yml exec -T backend \
  /app/docker-entrypoint.sh /app/bin/import_extended_tools \
  --file1 /app/sources/eea.climateadapt/data/tools_main.ods \
  --file2 /app/sources/eea.climateadapt/data/tools_extra.ods
```

Or via Python module:

```bash
docker compose -f backend/docker-compose.yml exec -T backend \
  /app/docker-entrypoint.sh /app/bin/python3 -m eea.climateadapt.scripts.import_extended_tools \
  --file1 /app/sources/eea.climateadapt/data/tools_main.ods \
  --file2 /app/sources/eea.climateadapt/data/tools_extra.ods
```

#### Commit Changes to ZODB:

```bash
docker compose -f backend/docker-compose.yml exec -T backend \
  /app/docker-entrypoint.sh /app/bin/import_extended_tools \
  --file1 /app/sources/eea.climateadapt/data/tools_main.ods \
  --file2 /app/sources/eea.climateadapt/data/tools_extra.ods \
  --commit
```

### CLI Arguments

| Argument | Default | Description |
|---|---|---|
| `--file1` | `/app/sources/eea.climateadapt/data/tools_main.ods` | Path to main metadata ODS or CSV file |
| `--file2` | `/app/sources/eea.climateadapt/data/tools_extra.ods` | Path to extra fields ODS file (optional) |
| `--commit` | `False` | When set, commits transactions to ZODB; otherwise runs dry-run |
| `--portal` | `cca` | Plone portal ID |
| `--zope-conf` | `/app/etc/relstorage.conf` | Path to Zope / RelStorage configuration file |

---

### 2. From Plone Web Management View

1. Navigate to:
   ```
   http://cca.localhost/cca/@@tool_extendfields_372446
   ```
2. In the form:
   - **Select Main Metadata file**: Upload the main `.ods` or `.csv` file.
   - **Select Extra Fields file**: (Optional) Upload the extra fields `.ods` file.
3. Click **Import Extended Tools**.
4. The page will execute the import, commit the transaction, and render a table showing the status, external ID, title, and link for each imported tool.

# Admin Views

All views below require `cmf.ManagePortal` permission unless noted otherwise.

## `configure.zcml` — Admin Views

### `@@gopdb`
**Class:** `eea.climateadapt.browser.adminp6.GoPDB`

Drops into a `pdb` debugger session on the current context. Useful for interactive debugging in the running Zope process.

---

### `@@inspect_catalog`
**Class:** `eea.climateadapt.browser.adminp6.InspectCatalog`

Looks up the catalog record for the current object's path and redirects to the ZMI `manage_objectInformation` page for that record ID. Useful for inspecting raw catalog metadata.

**URL pattern:** `https://climate-adapt.eea.europa.eu/<path-to-object>/@@inspect_catalog`

---

### `@@reindex_folder`
**Class:** `eea.climateadapt.browser.adminp6.ReindexFolder`

Reindexes the current folder and all its children recursively. Reindexes all catalog indexes. Disables CSRF protection.

---

### `@@reindex_ct`
**Class:** `eea.climateadapt.browser.adminp6.ReindexContentType`

Reindexes all objects of a given content type under the current path.

**Parameters (POST form data):**
- `ct` — Content type name (e.g. `Document`)
- `idxs` — Specific indexes to reindex (optional; if omitted, all indexes are updated)

---

### `@@local_roles_report`
**Class:** `eea.climateadapt.browser.local_roles_report.LocalRolesReportView`

Reports all local roles defined across the portal.

**Parameters (query string):**
- `full=1` — Include owner roles in the report
- `format=csv` — Download report as CSV instead of HTML

---

### `@@document_workflows`
**Class:** `eea.climateadapt.browser.document_workflows.DocumentWorkflowsView`

Visualizes workflow associations for all content types — shows which workflows are assigned to each portal type, their states, transitions, and permission mappings. Rendered via `pt/document_workflows.pt`.

---

### `@@import_mission_sigs`
**Class:** `eea.climateadapt.browser.import_mission.MissionSigImporter`

Imports signatory profiles from a zip file located in the package's `data/2024` directory. Creates `mission_signatory_profile` objects and nested `Folder`/`File` structures. Disables CSRF protection.

---

## `ecde.zcml` — ECDE Indicator Views (Public)

All views below are publicly accessible (`zope2.View`).

### `@@c3s_indicators_overview`
**Class:** `eea.climateadapt.browser.ecde.C3sIndicatorsOverview`

Displays a C3S (Copernicus Climate Change Service) indicators overview. Template: `pt/c3s_indicators_overview.pt`.

---

### `@@c3s_indicators_glossary_table`
**Class:** `eea.climateadapt.browser.ecde.C3sIndicatorsOverview`

Displays the glossary table for C3S indicators. Template: `pt/c3s_indicators_glossary_table.pt`.

---

### `@@c3s_indicators_listing`
**Class:** `eea.climateadapt.browser.ecde.C3sIndicatorsListing`

Displays a listing of C3S indicators. Template: `pt/c3s_indicators_listing.pt`.

---

### `@@c3s_disclaimer`
**Class:** `eea.climateadapt.browser.ecde.C3sIndicatorsOverview`

Displays the C3S disclaimer. Template: `pt/c3s_disclaimer.pt`.

---

## `update_migrations.zcml` — Migration Views

### `@@fix_mip_lang`
**Class:** `eea.climateadapt.browser.migrate.FixMipSigLangs`

Fixes the language setting on `mission_signatory_profile` objects under `/cca/en` to `"en"` and reindexes the `Language` index. Requires `write=1` in POST form to actually perform the write; otherwise raises `ValueError`. Disables CSRF protection.

---

## `configure.zcml` — Other Migrations

### `@@migrate-absolute-urls`
**Class:** `eea.climateadapt.browser.migrate.MigrateAbsoluteURLs`

Migrates absolute URLs in block fields to `resolveuid` references. Searches all objects implementing `IBlocks` behavior (optionally filtered by modification date via `?days=N`). Redirects back to the context URL after completion. Disables CSRF protection.

---

### `@@impact_filters_262157`
**Class:** `eea.climateadapt.browser.migrate.ImpactFiltersNew`

Updates climate impact metadata on content items from a CSV upload. Reads columns: `UID`, `URL`, `Title`, `Keywords`, `Sectors`, `Impacts`, `Elements`, and impact flags (`EXTREME HEAT`, `EXTREME COLD`, `WILDFIRES`, `NON SPECIFIC`). Requires a CSV file upload via `fileToUpload` form field.

---

### `@@archive-items-2025-294148`
**Class:** `eea.climateadapt.browser.migrate.ArchiveItems294148`

Identifies and optionally archives items under `#294148` — content types (`eea.climateadapt.publicationreport`, `eea.climateadapt.aceproject`, `eea.climateadapt.notypeselected`) published before 2016. Requires `publicationreport=1` or `aceproject=1` in the form; use `doarchive=1` to actually perform the archival transition.

---

## `configure.zcml` — Collective ExportImport (Public)

All views are accessible at the site root (`/`) under `collective.exportimport`.

### `@@export_content`
**Class:** `eea.climateadapt.browser.exportimport.CustomExportContent`
**Template:** `collective.exportimport:templates/export_content.pt`

Customized content export that adds `modified` date filtering (`?from=N` where N is number of days) and exports marker interfaces (`IBalticRegionMarker`, `ICCAcountry`, etc.) and annotations (`c3s_json_data`, `broken_links_data`) as extra fields.

---

### `@@import_content`
**Class:** `eea.climateadapt.browser.exportimport.CustomImportContent`
**Template:** `collective.exportimport:templates/import_content.pt`

Customized content import that restores marker interfaces and annotations exported by `@@export_content`.

---

### `@@export_ordering`
**Class:** `eea.climateadapt.browser.exportimport.FixedExportOrdering`
**Template:** `collective.exportimport:templates/export_other.pt`

Exports the ordering (position in parent) of all objects in the portal. The fix addresses ordering for objects inside ordered containers.

---

### `@@import_translations`
**Class:** `eea.climateadapt.browser.exportimport.CustomImportTranslations`
**Template:** `collective.exportimport:templates/import_translations.pt`

Customized translation import that links translation groups, ensuring each group has at least two items before linking.

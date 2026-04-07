# EEA Climate Adapt (`eea.climateadapt`)

## Project Overview
`eea.climateadapt` is a **Plone add-on** that powers the European Environment Agency's (EEA) Climate-ADAPT platform. It provides the backend logic, content types, and integrations for the Climate-ADAPT website.

The project is currently in a state of transition or hybrid operation, supporting both **Classic Plone** (server-side rendering) and **Plone 6 / Volto** (React-based frontend), as evidenced by the presence of Volto layout definitions and migration scripts.

## Architecture & Technologies
*   **Framework:** Plone CMS (Python, Zope).
*   **Frontend Integration:** Volto (React) via `plone.restapi`. Extensive Volto block layouts are defined in `eea/climateadapt/behaviors/volto_layout.py`.
*   **Configuration:** ZCML (Zope Configuration Markup Language) is heavily used for wiring views, adapters, and subscribers.
*   **Database:** ZODB (Zope Object Database).
*   **Async Processing:** Uses `bullmq` and `redis` for asynchronous tasks (e.g., seemingly related to `eea.climateadapt.scripts.cli_arcgis_client` or similar background jobs).
*   **Linting/Formatting:** `ruff` is the configured linter and formatter (see `pyproject.toml`).

## Key Directories & Files

*   `eea/climateadapt/`: Main package source.
    *   `configure.zcml`: Main ZCML configuration entry point.
    *   `interfaces.py`: Marker interfaces for content types and views.
    *   `browser/`: Browser views, viewlets, and resources (Classic Plone UI).
    *   `behaviors/`: Dexterity behaviors, including Volto layout definitions (`volto_layout.py`).
    *   `restapi/`: Custom endpoints for `plone.restapi`.
    *   `upgrades/`: Migration steps (GenericSetup).
    *   `locales/`: Translation files.
*   `setup.py`: Package metadata and dependencies.
*   `pyproject.toml`: Configuration for build tools and linters (`ruff`).
*   `docs/INSTALL.txt`: Installation instructions.

## Development & Usage

### Installation
The project uses `buildout` for dependency management and instance creation, standard for Plone projects.
See `docs/INSTALL.txt` for detailed steps.

1.  **Dependencies:** Ensure system dependencies for Plone are installed (libxml2, libxslt, etc.).
2.  **Buildout:**
    ```bash
    # (Example command - check specific buildout config)
    ./bin/buildout
    ```

### Running the Instance
```bash
./bin/instance fg
```
*(Note: Requires a configured buildout environment)*

### Testing
Tests are run using `zope.testrunner` (usually wrapped by a script in `bin/`).
```bash
./bin/test -s eea.climateadapt
```

### Code Style
The project uses `ruff` for code style.
```bash
ruff check .
ruff format .
```

## Contributing
*   **Repository:** Fork from `collective/eea.climateadapt`.
*   **Branching:** Submit Pull Requests to the `master` branch.
*   **Changelog:** Update `docs/HISTORY.txt` with a summary of changes.
*   **Conventions:**
    *   Use ZCML for component registration.
    *   Follow Plone best practices for Dexterity content types.
    *   Respect existing code style (checked by `ruff`).

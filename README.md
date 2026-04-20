# EEA Climate Adapt (`eea.climateadapt`)

[![Build Status](http://ci.eionet.europa.eu/job/eea.climateadapt-www/badge/icon)](http://ci.eionet.europa.eu/job/eea.climateadapt-www/lastBuild)

`eea.climateadapt` is a **Plone add-on** that powers the European Environment Agency's (EEA) Climate-ADAPT platform. It provides the backend logic, content types, and integrations for the Climate-ADAPT website.

The project supports both **Classic Plone** (server-side rendering) and **Plone 6 / Volto** (React-based frontend).

## Architecture & Technologies
*   **Framework:** Plone CMS (Python, Zope).
*   **Frontend Integration:** Volto (React) via `plone.restapi`. Extensive Volto block layouts are defined in `eea/climateadapt/behaviors/volto_layout.py`.
*   **Async Processing:** Uses `bullmq` and `redis` for asynchronous tasks related to automatic translation.
*   **Micro-services:**
    *   **climateadapt-async-translate**: A Node.js service managing an asynchronous queue for the automatic translation process.
    *   **volto-blocks-converter**: A service used to convert Volto blocks (JSON) to HTML and back.

## Automatic Translation Workflow

The translation process is handled asynchronously via the following steps:

1.  **Triggering Translation**: Editors change or publish a page, scheduling "call etranslation" jobs.
2.  **Job: `call_etranslation`**: Processed by the `climateadapt-async-translate` service, which calls back into Plone (`@@call-etranslation`).
3.  **External Translation**: Plone calls the European Commission's eTranslation web service.
4.  **Callback**: eTranslation calls a Plone callback view (`@@translate-callback`) with the translated HTML.
5.  **Job: `save_translated_html`**: The async service receives the content and calls back into Plone (`@@save-etranslation`) to update the translated page.

## Key Directories & Files

*   `eea/climateadapt/`: Main package source.
    *   `configure.zcml`: Main ZCML configuration entry point.
    *   `interfaces.py`: Marker interfaces for content types and views.
    *   `browser/`: Browser views, viewlets, and resources (Classic Plone UI).
    *   `behaviors/`: Dexterity behaviors, including Volto layout definitions (`volto_layout.py`).
    *   `restapi/`: Custom endpoints for `plone.restapi`.
    *   `upgrades/`: Migration steps (GenericSetup).
*   `setup.py`: Package metadata and dependencies.
*   `pyproject.toml`: Configuration for build tools and linters (`ruff`).

## Development & Usage

### Installation & Orchestration
This project is intended to be run as part of the [eea.docker.plone-climateadapt](https://github.com/eea/eea.docker.plone-climateadapt) orchestration.

Please refer to that repository for detailed instructions on how to set up the full stack (Backend, Frontend, Redis, and Translation micro-services) using Docker and `docker-compose`.

In a typical development environment:
1.  Clone the orchestration repository.
2.  The source code of this package is usually mapped into the `backend/sources/eea.climateadapt` directory.
3.  Use `docker compose` to start the services.

### Running Tests
To run tests within the Docker environment:
```bash
docker compose exec backend ./bin/test -s eea.climateadapt
```

### Code Style
The project uses `ruff` for code style.
```bash
docker compose exec backend ruff check .
docker compose exec backend ruff format .
```

## Source code
- Latest source code: [https://github.com/eea/eea.climateadapt](https://github.com/eea/eea.climateadapt)

## Copyright and license
The Initial Owner of the Original Code is European Environment Agency (EEA). All Rights Reserved.

The EEA Climate Adapt (the Original Code) is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

More details under `docs/LICENSE.txt`.

## Funding
[EEA](http://www.eea.europa.eu/) - European Environment Agency (EU)

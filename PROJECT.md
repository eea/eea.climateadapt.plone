# Climate-ADAPT Project Documentation

This project is a complex system based on **Plone** (backend) and **Volto** (frontend). It manages the [Climate-ADAPT website](https://climate-adapt.eea.europa.eu/) content and its automatic translation process across all official EU languages.

## Architecture Overview

The project consists of a Plone backend with several custom add-ons and two supporting micro-services.

### Backend
- **Core Product**: `sources/eea.climateadapt` - This is the main Plone add-on containing the business logic, content types, and translation management.
- **Environment**: Local development uses `docker-compose`. Source code is typically mapped into the `sources/` subfolder of the backend container.

### Micro-services
- **climateadapt-async-translate**: A Node.js service using [BullMQ](https://bullmq.io/) and TypeScript. it manages an asynchronous queue for the automatic translation process.
- **volto-blocks-converter**: A service used to convert Volto blocks (JSON) to HTML and back. This is primarily used to prepare content for the eTranslation service and to process the translated results.

## Automatic Translation Workflow

The translation process is handled asynchronously to ensure a responsive user interface and to manage the limitations and potential latency of the external eTranslation service.

### 1. Triggering Translation
When an editor changes or publishes a page, "call etranslation" jobs are scheduled for each supported language.

### 2. Job: `call_etranslation`
Processed by the `climateadapt-async-translate` service:
- The service receives a job to translate content.
- It calls back into a Plone view (`@@call-etranslation`).
- **Rationale**: Plone handles the actual call to the European Commission's eTranslation service because it holds the necessary authentication credentials and service configuration.

### 3. External Translation
- The Plone view calls the eTranslation web service.
- eTranslation processes the request.

### 4. Callback from eTranslation
- Once translation is complete, the eTranslation service calls a Plone callback view (`@@translate-callback`).
- This view receives the translated HTML.
- It schedules a new BullMQ job: `save_translated_html`.

### 5. Job: `save_translated_html`
Processed by the `climateadapt-async-translate` service:
- The service receives the translated content.
- It calls back into a Plone view (`@@save-etranslation`).
- Plone creates or updates the translated page using the provided data.

## Key Development Areas

- **Automatic Translation**: This is a critical part of the system and a focus for ongoing improvements.
- **Content Conversion**: Refining how Volto blocks are represented as HTML for translation and how they are re-composed into Volto JSON after translation.
- **Reliability**: Improving the robustness of the async queue and handling various edge cases in the translation lifecycle.

## Technical Notes

- **Environment & Execution**: The AI agent operates **outside** the Docker container. All commands intended to run within the backend environment (e.g., running scripts, migrations, or tests) MUST be wrapped in `docker compose exec backend`.
- **Python Executable**: Inside the backend container, the correct Python to use is `/app/bin/python3`, which has the full environment with all dependencies.
- **Authentication**: The communication between the Node.js services and Plone is protected by a shared `TRANSLATION_AUTH_TOKEN`.
- **Queues**: BullMQ queues are used to decouple the long-running translation tasks from the main CMS operations.

## Development Lessons Learnt

### Zope Configuration Parsing
- **Schema Sensitivity**: Standard `ZConfig.loadSchema` or `ZODB.config.storageFromFile` might fail in Zope/Plone environments because they don't handle Zope-specific schema keys (like `instancehome`) or conditional imports (like `tempstorage` in `wsgischema.xml`).
- **Correct Configuration Loader**: For Zope 5+ (WSGI), use `Zope2.Startup.options.ZopeWSGIOptions` to correctly parse a Zope configuration file (`zope.conf` or `relstorage.conf`) without needing to fully initialize the Zope application.
- **Efficient Metadata Extraction**: Use `ZODB.utils.get_pickle_metadata` to extract class names from ZODB records without unpickling the entire object. This is significantly faster and avoids dependency issues during database scanning.

## Automated GitHub Interactions

When using the `gh` (GitHub CLI) utility for automated workflows (e.g., creating PRs from scripts or agents), follow these best practices:

### 1. Initial PR Creation
Always provide both the title and body during creation to minimize subsequent API calls:
```bash
gh pr create --title "Your Title" --body "Your detailed PR description"
```

### 2. Handling GraphQL Errors
Some repositories (like `eea.climateadapt.plone`) may have legacy "Projects (classic)" settings that cause `gh pr edit` to fail with GraphQL errors. If this happens, fallback to the GitHub REST API using `gh api`:

**To update a PR title and body:**
```bash
gh api -X PATCH /repos/{owner}/{repo}/pulls/{pr_number} \
  -f title="New Title" \
  -f body="New Body Content"
```

### 3. Verification
To verify the content of a PR programmatically (e.g., ensuring the body was written):
```bash
gh pr view {pr_number} --json title,body
```

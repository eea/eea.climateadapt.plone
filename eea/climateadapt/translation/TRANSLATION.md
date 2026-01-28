# Translation Process Documentation

This document describes the automatic translation workflow in `eea.climateadapt`, focusing on the core logic in `core.py` and the API views in `views.py`.

## Architecture Overview

The translation system is asynchronous and relies on:
1.  **Plone (Backend)**: Orchestrates the workflow and stores content.
2.  **eTranslation**: The European Commission's machine translation service (SOAP-based).
3.  **Async Translate Service (Node.js)**: Manages BullMQ queues to handle long-running tasks.
4.  **Converter Service**: Handles Volto blocks to HTML and HTML to Plone content conversions.

```mermaid
sequenceDiagram
    participant P as Plone (Backend)
    participant Q as Redis (BullMQ)
    participant W as Async Service (Worker)
    participant ET as eTranslation (EC)

    Note over P: Object created/modified
    P->>Q: queue_translate (call_etranslation)
    Q->>W: Fetch job
    W->>P: POST @@call-etranslation
    P->>ET: SOAP Request (translate)
    Note over ET: Machine Translation
    ET-->>P: POST @@translate-callback (translated HTML)
    P->>Q: queue_job (save_translated_html)
    Q->>W: Fetch job
    W->>P: POST @@save-etranslation (ingest HTML)
    Note over P: Object Updated
```

## Core Components (`core.py`)

### Job Queuing
- `queue_job(queue_name, job_name, data)`: Schedules a task for the external queue (Redis/BullMQ) at the end of the transaction.
- `queue_translate(obj, language)`: The entry point to start translating an object. It converts Volto blocks to HTML and queues the `call_etranslation` job.

### eTranslation Interaction
- `call_etranslation_service(html, obj_path, target_languages)`: Makes the actual SOAP call to eTranslation. It uses the `ETRANSLATION_SOAP_SERVICE_URL` and credentials configured in the environment.
- `destinations`: Configured to point back to the Plone site's `@@translate-callback`.

### Content Ingestion
- `ingest_html(trans_obj, html)`: The main logic for applying translated HTML back to a Plone object.
- `get_content_from_html(html, language)`: Calls the external converter service to transform HTML back into structured Plone data (including Volto blocks).
- `save_field_data(canonical, trans_obj, fielddata)`: Iterates over schemata and applies translated values to fields, respecting language-independent settings.

### Translation Management
- `setup_translation_object(canonical, language, request)`: Ensures a translation object exists in the correct path and is registered with the `TranslationManager`.
- `sync_translation_paths(...)`: Handles moving/renaming translations when the canonical (English) object is moved.

## API Views (`views.py`)

These views provide the interface for the Async Translate Service and eTranslation callbacks.

- `@@call-etranslation`: Called by the worker to trigger the SOAP call.
- `@@translate-callback`: The endpoint registered with eTranslation. It receives the translated HTML and queues it for saving.
- `@@save-etranslation` (via `SaveTranslationHtml` class): Called by the worker to finalise the ingestion of translated content into Plone.
- `@@tohtml`: Converts a Plone object's fields to a unified HTML representation suitable for translation. It uses the converter service for Volto blocks.
- `@@sync-translated-paths`: Interface to trigger path synchronization after move operations.

## Key Utilities

- `get_blocks_as_html(obj)`: Helper in `core.py` to extract Volto blocks as HTML via the converter service.
- `copy_missing_interfaces(en_obj, trans_obj)`: ensures behaviors and interfaces are consistent across translations.
- `sync_translation_state(trans_obj, en_obj)`: Synchronizes workflow state (e.g., Published) and effective dates.

## Security

Communication between the micro-services and Plone is protected by `TRANSLATION_AUTH_TOKEN`, checked via `check_token_security(request)`.

## Serial ID Mechanism (Conflict Resolution)

To prevent database conflicts and redundant translations when an object is modified multiple times in a short period, a "Serial ID" mechanism is used.

### Purpose
The Serial ID acts as a version counter for the object's content. It ensures that a translation job processed by the worker matches the *current* state of the object. If the object has been modified since the job was queued, the job is considered "stale" and is invalid.

### Components
1.  **`ISerialId` Interface** (`versions.py`): An integer annotation stored on the object.
2.  **Increment Subscriber** (`versions.zcml`): Listens for `IObjectModifiedEvent` and increments the object's `ISerialId` by 1.
3.  **Job Payload**: When `queue_translate` is called, the *current* `serial_id` is embedded in the job data (specifically in the `obj_path` query parameter).

### Validation Process
When the async worker picks up a `call_etranslation` job and calls back the Plone view `@@call-etranslation`:
1.  The view extracts the `serial_id` from the request.
2.  It retrieves the current `ISerialId` from the target object.
3.  **Check**: If `current_serial_id > job_serial_id`, the object has changed since the job was scheduled.
4.  **Action**: The job is skipped (returns a "skipped" status), preventing the eTranslation call and avoiding potential Write conflicts on the outdated content.

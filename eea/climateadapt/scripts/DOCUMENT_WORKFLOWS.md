# Workflow and Content Type Documentation Script

This script is a Zope command-line utility designed to document the association between content types and workflows within the Climate-ADAPT portal, including detailed information about workflow states and transitions.

## Rationale

Understanding the lifecycle of different content types is crucial for both developers and editors. This script provides a comprehensive overview of how each content type is managed through its assigned workflow, making it easier to audit permissions and understand the automatic translation triggers.

## Features

- **Content Type Mapping**: Lists all active Dexterity content types and their assigned workflows.
- **Workflow Deep Dive**: For each workflow, it reports:
    - Initial state.
    - All possible states and their titles.
    - All transitions, including their titles, source states, and destination states.
- **Multiple Output Formats**: Supports both human-readable console output and machine-readable JSON/CSV export.
- **Fault Tolerance**: Safely handles cases where a content type might not have an assigned workflow or if workflow definitions are missing.

## How to Run

The script is registered as a console script and should be run within the Docker environment.

### Setup

For the console script to be available, you must first install the package dependencies within the container (this registers the entry points):

```bash
docker compose exec backend bin/pip install -r requirements-mxdev.txt
```

### Execution

Run the script using `docker compose exec`. Note that you must provide the `--zope-conf` argument pointing to the configuration file.

```bash
# Standard console report
docker compose exec backend /app/docker-entrypoint.sh bin/document_workflows --portal cca --zope-conf etc/relstorage.conf

# Generate JSON report
docker compose exec backend /app/docker-entrypoint.sh bin/document_workflows --portal cca --zope-conf etc/relstorage.conf --json workflows.json
```

## Implementation Details

- **Tool Access**: Uses `portal_types` to iterate over content types and `portal_workflow` to retrieve workflow associations and definitions.
- **Workflow Analysis**: Explores `DCWorkflow` objects to extract states, transitions, and logic (like guards or variables, if needed).
- **Interface-Based**: Focuses on Dexterity content types but can be extended to include legacy CMF types if any remain.

## Output Format (Console Example)

```text
Content Type: News Item
  Workflow: news_workflow
  Initial State: private
  States:
    - private (Private)
    - pending (Pending Review)
    - published (Published)
  Transitions:
    - submit (Submit for publication): private -> pending
    - publish (Publish): pending -> published
    - retract (Retract): published -> private
```

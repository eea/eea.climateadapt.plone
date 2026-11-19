# Import Extended Tool categories

`import_tool_types` assigns the `tool_type` field on existing Extended Tools from
the `Navigator_tool_icon_assignment.ods` spreadsheet. It matches rows to content
by `Tool ID` / `external_id` and never changes other content fields.

The expected first-sheet columns are:

- `Tool ID`
- `Tool name`
- `Tool type (category)`

## Browser upload

Open the target Extended Tools folder and visit:

```text
@@import-tool-types
```

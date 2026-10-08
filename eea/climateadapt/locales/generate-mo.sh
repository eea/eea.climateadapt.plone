#!/bin/sh

set -eu

if ! command -v msgfmt >/dev/null 2>&1; then
  echo "Error: msgfmt is not installed or is not available on PATH." >&2
  exit 127
fi

# Generate mo file from any po files in any folders
find . -mindepth 3 -path "*/LC_MESSAGES/*.po" -type f -exec sh -c '
  for po do
    msgfmt -o "${po%.po}.mo" "$po"
  done
' sh {} +

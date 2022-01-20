#!/bin/sh

# Generate mo file from any po files in any folders
for PO in $(find */LC_MESSAGES/ -name "*.po"); do
  msgfmt -o ${PO/%.po/.mo} $PO;
done



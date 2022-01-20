#!/usr/bin/env bash
cd $(dirname $0)
CATALOGNAME="collective.cover"

for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do

    if test -d $lang/LC_MESSAGES; then

        PO=$lang/LC_MESSAGES/${CATALOGNAME}.po
		touch $PO
    fi
done

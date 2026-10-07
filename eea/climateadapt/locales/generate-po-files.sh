#!/usr/bin/env bash
#
# Shell script to generate .po files.
#

set -euo pipefail

if ! command -v i18ndude >/dev/null 2>&1; then
    echo "Error: i18ndude is not installed or is not available on PATH." >&2
    echo "Activate the project's Python/buildout environment and try again." >&2
    exit 127
fi

declare -a list=(
              "eea.cca"
              "eea.climateadapt"
              "eea.climateadapt.menu"
              "eea.climateadapt.frontpage"
              "eea.climateadapt.observatory.frontpage"
              )

length=${#list[@]}

for lang in $(find ./ -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        echo $lang
        for (( j=0; j<length; j++ ));
        do
	          domain=${list[$j]}
            touch $lang/LC_MESSAGES/$domain.po
            i18ndude sync --pot $domain.pot $lang/LC_MESSAGES/$domain.po
        done
    fi
done

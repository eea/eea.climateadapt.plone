#!/bin/sh
#
# Shell script to generate .po files.
#

declare -a list=("eea.climateadapt" "eea.climateadapt.menu" "eea.climateadapt.frontpage")

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

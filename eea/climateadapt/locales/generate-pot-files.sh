#!/usr/bin/env bash

i18ndude rebuild-pot \
	--pot eea.climateadapt.pot \
  --create eea.climateadapt \
	--exclude "behaviors profiles tiles *.zcml contentrules.py export_portaltypes.pt keywords-admin.pt special-tags-admin.pt" \
	../../

  #--exclude "behaviors profiles tiles profiles.zcml keywords-admin.pt special-tags-admin.pt" \

i18ndude rebuild-pot \
	--pot eea.climateadapt.admin.pot \
  --create eea.climateadapt.admin \
	../../

i18ndude rebuild-pot \
	--pot eea.climateadapt.frontpage.pot \
  --create eea.climateadapt.frontpage \
	--exclude "behaviors browser profiles tiles *.zcml contentrules.py overrides.py export_portaltypes.pt keywords-admin.pt special-tags-admin.pt" \
	../../

#!/usr/bin/env bash

i18ndude rebuild-pot \
	--pot eea.climateadapt.pot \
  --create eea.climateadapt \
	--exclude "behaviors profiles *.zcml contentrules.py export_portaltypes.pt keywords-admin.pt special-tags-admin.pt" \
	../../

  #--exclude "behaviors profiles tiles profiles.zcml keywords-admin.pt special-tags-admin.pt" \

i18ndude rebuild-pot \
	--pot eea.climateadapt.admin.pot \
  --create eea.climateadapt.admin \
	../../

i18ndude rebuild-pot \
	--pot eea.climateadapt.frontpage.pot \
  --create eea.climateadapt.frontpage \
	--exclude "health*" \
	../theme/climateadaptv2/

i18ndude rebuild-pot \
	--pot eea.climateadapt.observatory.frontpage.pot \
  --create eea.climateadapt.observatory.frontpage \
	--exclude "index.html page.html" \
	../theme/climateadaptv2/

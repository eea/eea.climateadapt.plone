#!/usr/bin/env bash

i18ndude rebuild-pot \
	--pot eea.climateadapt.observatory.frontpage.pot \
  --create eea.climateadapt.observatory.frontpage \
	--exclude "index.html page.html" \
	../

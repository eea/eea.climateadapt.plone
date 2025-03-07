all: build-docker publish
	@echo "Building"

.PHONY: build-docker
build-docker:
	docker build . --no-cache -t tiberiuichim/climateadapt-async-translate:latest

.PHONY: publish
publish:
	docker push tiberiuichim/climateadapt-async-translate:latest

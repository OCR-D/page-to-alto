PYTHON = python3
PIP = pip3
DOCKER = docker

# Base image for the docker image
DOCKER_BASE_IMAGE ?= docker.io/ocrd/core:latest
# Tag to publish docker image
DOCKER_TAG ?= ocrd/page2alto

# BEGIN-EVAL makefile-parser --make-help Makefile

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    submodules   initiate submodules"
	@echo "    deps         Install deps"
	@echo "    install      Install ocrd_page_to_alto"
	@echo "    install-dev  Install ocrd_page_to_alto editable"
	@echo "    assets       Copy OCR-D/assets to tests/assets"
	@echo "    test         Run tests"
	@echo ""
	@echo "  Variables"
	@echo ""

# END-EVAL

# initiate submodules
submodules:
	git submodule update --init

# Install deps
deps:
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

deps-dev:
	$(PIP) install -U pip
	$(PIP) install -r requirements.dev.txt

# Install ocrd_page_to_alto
install: deps
	$(PIP) install .

# Install ocrd_page_to_alto editable
install-dev: deps deps-dev
	$(PIP) install -e .

# Copy OCR-D/assets to tests/assets
assets: submodules
	rm -rf tests/assets
	mkdir -p tests/assets
	cp -r repo/assets/data/* tests/assets
	cp -r repo/page-alto-resources/* tests/assets

# Run tests
test:
	$(PYTHON) -mpytest tests

# Build docker image
docker:
	$(DOCKER) build \
	--build-arg DOCKER_BASE_IMAGE=$(DOCKER_BASE_IMAGE) \
	--build-arg VCS_REF=$$(git rev-parse --short HEAD) \
	--build-arg BUILD_DATE=$$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
	-t $(DOCKER_TAG) .

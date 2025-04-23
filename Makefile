DATE    = $(shell date)
PYTHON  = $(shell which python)

TOPDIR = $(shell pwd)
SCRIPTDIR = $(TOPDIR)/scripts

IQE_CMD = 'iqe tests plugin --debug cost_management -k test_api -m cost_smoke'

DOCKER := $(shell command -v docker 2> /dev/null)
PODMAN := $(shell command -v podman 2> /dev/null)

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help                to show this message"
	@echo "  install             to install the client egg"
	@echo "  clean               to remove client egg"
	@echo "  test                to run unit tests"
	@echo "  run-iqe             runs iqe tests with local changes. (Defaults to smoke tests.)"
	@echo "                          @param IQE_CMD - The iqe command you want to run defaults to:"
	@echo "                          ($(IQE_CMD))"
	@echo "  run-iqe-local       runs a locally modified hccm-plugin with local nise changes."
	@echo "                          @param IQE_CMD - The iqe command you want to run defaults to:"
	@echo "                          ($(IQE_CMD))"

install: clean
	$(PYTHON) setup.py build -f
	$(PYTHON) setup.py install -f

clean:
	-rm -rf dist/ build/ koku_nise.egg-info/
ifdef DOCKER
	docker stop iqe-nise 2> /dev/null | true
	docker rm iqe-nise 2> /dev/null | true
endif
ifdef PODMAN
	podman stop 2> /dev/null | true
	podman rm iqe-nise 2> /dev/null | true
endif


lint:
	pre-commit run --all-files

run-iqe:
	cd scripts; ./iqe_container.sh $(IQE_CMD)

run-iqe-local:
	cd scripts; ./local_iqe_container.sh $(IQE_CMD)

requirements:
	uv sync

DATE    = $(shell date)
PYTHON  = $(shell which python)

TOPDIR = $(shell pwd)
IQE_CMD = 'iqe tests plugin --debug hccm -k test_api -m hccm_smoke'

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help                to show this message"
	@echo "  install             to install the client egg"
	@echo "  clean               to remove client egg"
	@echo "  test                to run unit tests"
	@echo "  run-iqe             ro runs iqe tests with local changes. (Defaults to smoke tests.)"
	@echo "                          @param IQE_CMD - The iqe command you want to run defaults to: ($(IQE_CMD))"

install: clean
	$(PYTHON) setup.py build -f
	$(PYTHON) setup.py install -f

clean:
	-rm -rf dist/ build/ koku_nise.egg-info/
	docker stop iqe-nise | true
	docker rm iqe-nise | true

test:
	tox -e py36

lint:
	tox -e lint

run-iqe:
	cd scripts; ./iqe_container.sh $(IQE_CMD)
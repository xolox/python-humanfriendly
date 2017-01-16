# Makefile for the 'humanfriendly' package.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: September 28, 2016
# URL: https://humanfriendly.readthedocs.io

# The following defaults are based on my preferences, but possible for others
# to override thanks to the `?=' operator.
WORKON_HOME ?= $(HOME)/.virtualenvs
VIRTUAL_ENV ?= $(WORKON_HOME)/humanfriendly
PATH := $(VIRTUAL_ENV)/bin:$(PATH)
MAKE := $(MAKE) --no-print-directory
SHELL = bash

default:
	@echo 'Makefile for humanfriendly'
	@echo
	@echo 'Usage:'
	@echo
	@echo '    make install    install the package in a virtual environment'
	@echo '    make reset      recreate the virtual environment'
	@echo '    make check      check coding style (PEP-8, PEP-257)'
	@echo '    make test       run the test suite, report coverage'
	@echo '    make tox        run the tests on all Python versions'
	@echo '    make readme     update usage in readme'
	@echo '    make docs       update documentation using Sphinx'
	@echo '    make publish    publish changes to GitHub/PyPI'
	@echo '    make clean      cleanup all temporary files'
	@echo

install:
	@test -d "$(VIRTUAL_ENV)" || mkdir -p "$(VIRTUAL_ENV)"
	@test -x "$(VIRTUAL_ENV)/bin/python" || virtualenv --quiet "$(VIRTUAL_ENV)"
	@test -x "$(VIRTUAL_ENV)/bin/pip-accel" || (pip install --quiet pip-accel && pip-accel install --quiet 'urllib3[secure]')
	@pip uninstall --yes humanfriendly &>/dev/null || true
	@pip install --quiet --editable .

reset:
	$(MAKE) clean
	rm -Rf "$(VIRTUAL_ENV)"
	$(MAKE) install

check: install
	@scripts/check-code-style.sh

test: install
	@pip-accel install --quiet --requirement=requirements-testing.txt coverage pytest-cov
	@py.test --cov
	@coverage combine
	@coverage html

tox: install
	@pip-accel install --quiet tox && tox

readme: install
	@pip-accel install --quiet cogapp && cog.py -r README.rst

docs: readme
	@pip-accel install --quiet sphinx
	cd docs && sphinx-build -nb html -d build/doctrees . build/html

publish: install
	git push origin && git push --tags origin
	$(MAKE) clean
	pip-accel install --quiet twine wheel
	python setup.py sdist bdist_wheel
	twine upload dist/*
	$(MAKE) clean

clean:
	@rm -Rf *.egg .cache .coverage build dist docs/build htmlcov
	@find -depth -type d -name __pycache__ -exec rm -Rf {} \;
	@find -type f -name '*.pyc' -delete

.PHONY: default install reset check test tox readme docs publish clean

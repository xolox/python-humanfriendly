# Makefile for the 'humanfriendly' module.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: May 25, 2015
# URL: https://humanfriendly.readthedocs.org

# The following defaults are based on my preferences, but possible for others
# to override thanks to the `?=' operator.
WORKON_HOME ?= $(HOME)/.virtualenvs
VIRTUAL_ENV ?= $(WORKON_HOME)/humanfriendly
ACTIVATE = . "$(VIRTUAL_ENV)/bin/activate"

# Sometimes I like to use Bash syntax extensions :-).
SHELL = bash

default:
	@echo "Makefile for the 'humanfriendly' package"
	@echo
	@echo 'Commands:'
	@echo
	@echo '    make install    install the package in a virtual environment'
	@echo '    make reset      recreate the virtual environment'
	@echo '    make clean      cleanup all temporary files'
	@echo '    make test       run the unit test suite'
	@echo '    make coverage   run the tests, report coverage'
	@echo '    make docs       update documentation using Sphinx'
	@echo '    make publish    publish changes to GitHub/PyPI'
	@echo
	@echo 'Variables:'
	@echo
	@echo "    WORKON_HOME = $(WORKON_HOME)"
	@echo "    VIRTUAL_ENV = $(VIRTUAL_ENV)"

install:
	test -d "$(WORKON_HOME)" || mkdir -p "$(WORKON_HOME)"
	test -x "$(VIRTUAL_ENV)/bin/python" || virtualenv "$(VIRTUAL_ENV)"
	test -x "$(VIRTUAL_ENV)/bin/pip" || ($(ACTIVATE) && easy_install pip)
	test -x "$(VIRTUAL_ENV)/bin/pip-accel" || ($(ACTIVATE) && pip install pip-accel)
	$(ACTIVATE) && pip uninstall --yes humanfriendly &>/dev/null || true
	$(ACTIVATE) && pip install --editable .

reset:
	rm -Rf "$(VIRTUAL_ENV)"
	make --no-print-directory install

clean:
	rm -Rf build dist docs/build htmlcov

test: install
	$(ACTIVATE) && python setup.py test

coverage: install
	$(ACTIVATE) && pip-accel install 'coverage >= 4.0a5'
	$(ACTIVATE) && coverage run setup.py test
	$(ACTIVATE) && coverage combine
	$(ACTIVATE) && coverage report
	$(ACTIVATE) && coverage html
	if [ "`whoami`" != root ] && which xdg-open &>/dev/null; then \
		xdg-open htmlcov/index.html &>/dev/null; \
	fi

docs: install
	test -x "$(VIRTUAL_ENV)/bin/sphinx-build" || ($(ACTIVATE) && pip-accel install sphinx)
	$(ACTIVATE) && cd docs && sphinx-build -b html -d build/doctrees . build/html

publish:
	git push origin && git push --tags origin
	make clean && python setup.py sdist upload

.PHONY: default install reset clean test coverage docs publish

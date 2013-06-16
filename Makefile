# Makefile for the 'humanfriendly' module.
#
# Author: Peter Odding <peter.odding@paylogic.eu>
# Last Change: June 17, 2013
# URL: https://github.com/xolox/python-human-friendly

default:
	@echo "Makefile for the 'humanfriendly' module"
	@echo
	@echo 'Usage:'
	@echo
	@echo '    make test       run the unit test suite'
	@echo '    make docs       update documentation using Sphinx'
	@echo '    make publish    publish changes to GitHub/PyPI'
	@echo '    make clean      cleanup all temporary files'
	@echo

test:
	python setup.py test

clean:
	rm -Rf build dist docs/build

docs:
	cd docs && make html

publish:
	git push origin && git push --tags origin
	make clean && python setup.py sdist upload

.PHONY: docs

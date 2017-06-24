#!/bin/bash -e

# Install the required Python packages.
pip install pip-accel
pip-accel install coveralls
pip-accel install --requirement=requirements-checks.txt
pip-accel install --requirement=requirements-tests.txt

# Install the project itself, making sure that potential character encoding
# and/or decoding errors in the setup script are caught as soon as possible.
LC_ALL=C pip-accel install .

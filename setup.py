#!/usr/bin/env python

# Setup script for the `humanfriendly' package.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: June 27, 2013
# URL: https://humanfriendly.readthedocs.org

import sys
from os.path import abspath, dirname, join
from setuptools import setup

# Find the directory where the source distribution was unpacked.
source_directory = dirname(abspath(__file__))

# Add the directory with the source distribution to the search path.
sys.path.append(source_directory)

# Import the module to find the version number (this is safe because we don't
# have any external dependencies).
from humanfriendly import __version__ as version_string

# Fill in the long description (for the benefit of PyPi)
# with the contents of README.rst (rendered by GitHub).
readme_file = join(source_directory, 'README.rst')
readme_text = open(readme_file, 'r').read()

setup(name='humanfriendly',
      version=version_string,
      description="Human friendly output for text interfaces using Python",
      long_description=readme_text,
      url='https://humanfriendly.readthedocs.org',
      author='Peter Odding',
      author_email='peter@peterodding.com',
      py_modules=['humanfriendly', 'humanfriendly_tests'],
      test_suite='humanfriendly_tests')

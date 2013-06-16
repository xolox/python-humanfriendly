#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup

# Fill in the long description (for the benefit of PyPi)
# with the contents of README.rst (rendered by GitHub).
readme_file = join(dirname(abspath(__file__)), 'README.rst')
readme_text = open(readme_file, 'r').read()

setup(name='humanfriendly',
      version='1.1',
      description="Human friendly command line output for Python",
      long_description=readme_text,
      url='https://pypi.python.org/pypi/humanfriendly',
      author='Peter Odding',
      author_email='peter@peterodding.com',
      py_modules=['humanfriendly', 'humanfriendly_tests'],
      test_suite='humanfriendly_tests')

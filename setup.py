#!/usr/bin/env python

"""Setup script for the `humanfriendly` package."""

# Author: Peter Odding <peter@peterodding.com>
# Last Change: August 4, 2016
# URL: https://humanfriendly.readthedocs.org

# Standard library modules.
import codecs
import os
import re
import sys

# De-facto standard solution for Python packaging.
from setuptools import find_packages, setup


def get_contents(*args):
    """Get the contents of a file relative to the source distribution directory."""
    with codecs.open(get_absolute_path(*args), 'r', 'utf-8') as handle:
        return handle.read()


def get_version(*args):
    """Extract the version number from a Python module."""
    contents = get_contents(*args)
    metadata = dict(re.findall('__([a-z]+)__ = [\'"]([^\'"]+)', contents))
    return metadata['version']


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)


def have_environment_marker_support():
    """
    Check whether setuptools has support for PEP-426 environment marker support.

    Based on the ``setup.py`` script of the ``pytest`` package:
    https://bitbucket.org/pytest-dev/pytest/src/default/setup.py
    """
    try:
        from pkg_resources import parse_version
        from setuptools import __version__
        return parse_version(__version__) >= parse_version('0.7.2')
    except Exception:
        return False

# Conditional importlib dependency for Python 2.6 and 3.0 when creating a source distribution.
install_requires = []
if 'bdist_wheel' not in sys.argv:
    if sys.version_info[:2] <= (2, 6) or sys.version_info[:2] == (3, 0):
        install_requires.append('importlib')

# Conditional importlib dependency for Python 2.6 and 3.0 when creating a wheel distribution.
extras_require = {}
if have_environment_marker_support():
    extras_require[':python_version == "2.6" or python_version == "3.0"'] = ['importlib']


setup(
    name='humanfriendly',
    version=get_version('humanfriendly', '__init__.py'),
    description="Human friendly output for text interfaces using Python",
    long_description=get_contents('README.rst'),
    url='https://humanfriendly.readthedocs.org',
    author='Peter Odding',
    author_email='peter@peterodding.com',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points=dict(console_scripts=[
        'humanfriendly = humanfriendly.cli:main'
    ]),
    test_suite='humanfriendly.tests',
    tests_require=[
        'capturer >= 2.1',
        'coloredlogs >= 2.0',
    ],
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Console',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Shells',
        'Topic :: System :: System Shells',
        'Topic :: System :: Systems Administration',
        'Topic :: Terminals',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
    ])

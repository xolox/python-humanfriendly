#!/usr/bin/env python

# Setup script for the `humanfriendly' package.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: October 20, 2018
# URL: https://humanfriendly.readthedocs.io

"""
Setup script for the `humanfriendly` package.

**python setup.py install**
  Install from the working directory into the current Python environment.

**python setup.py sdist**
  Build a source distribution archive.

**python setup.py bdist_wheel**
  Build a wheel distribution archive.
"""

# Standard library modules.
import codecs
import os
import re
import sys

# De-facto standard solution for Python packaging.
from setuptools import find_packages, setup


def get_contents(*args):
    """Get the contents of a file relative to the source distribution directory."""
    with codecs.open(get_absolute_path(*args), 'r', 'UTF-8') as handle:
        return handle.read()


def get_version(*args):
    """Extract the version number from a Python module."""
    contents = get_contents(*args)
    metadata = dict(re.findall('__([a-z]+)__ = [\'"]([^\'"]+)', contents))
    return metadata['version']


def get_install_requires():
    """Get the conditional dependencies for source distributions."""
    install_requires = []
    if 'bdist_wheel' not in sys.argv:
        if sys.version_info[:2] <= (2, 6) or sys.version_info[:2] == (3, 0):
            install_requires.extend(('importlib', 'unittest2'))
        if sys.version_info[:2] < (3, 3):
            install_requires.append('monotonic')
        if sys.platform == 'win32':
            install_requires.append('pyreadline')
    return sorted(install_requires)


def get_extras_require():
    """Get the conditional dependencies for wheel distributions."""
    extras_require = {}
    if have_environment_marker_support():
        # Conditional `importlib' and `unittest2' dependencies.
        expression = ':%s' % ' or '.join([
            'python_version == "2.6"',
            'python_version == "3.0"',
        ])
        extras_require[expression] = ['importlib', 'unittest2']
        # Conditional `monotonic' dependency.
        expression = ':%s' % ' or '.join([
            'python_version == "2.6"',
            'python_version == "2.7"',
            'python_version == "3.0"',
            'python_version == "3.1"',
            'python_version == "3.2"',
        ])
        extras_require[expression] = ['monotonic']
        # Conditional `pyreadline' dependency.
        expression = ':sys_platform == "win32"'
        extras_require[expression] = 'pyreadline'
    return extras_require


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


setup(
    name='humanfriendly',
    version=get_version('humanfriendly', '__init__.py'),
    description="Human friendly output for text interfaces using Python",
    long_description=get_contents('README.rst'),
    url='https://humanfriendly.readthedocs.io',
    author="Peter Odding",
    author_email='peter@peterodding.com',
    license='MIT',
    packages=find_packages(),
    entry_points=dict(console_scripts=[
        'humanfriendly = humanfriendly.cli:main',
    ]),
    install_requires=get_install_requires(),
    extras_require=get_extras_require(),
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
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

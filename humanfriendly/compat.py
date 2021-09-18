# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: September 17, 2021
# URL: https://humanfriendly.readthedocs.io

"""
Compatibility.

This module exposes compatibility aliases and functions.
"""
# Standard library modules.
import sys

__all__ = (
    'coerce_string',
    'is_string',
    'on_macos',
    'on_windows',
)


def coerce_string(value):
    """
    Coerce any value to a :class:`python3:str` string.

    :param value: The value to coerce.
    :returns: The value coerced to a Unicode string.
    """
    return str(value)


def is_string(value):
    """
    Check if a value is a :class:`python3:str` object.

    :param value: The value to check.
    :returns: :data:`True` if the value is a string, :data:`False` otherwise.
    """
    return isinstance(value, str)


def on_macos():
    """
    Check if we're running on Apple MacOS.

    :returns: :data:`True` if running MacOS, :data:`False` otherwise.
    """
    return sys.platform.startswith('darwin')


def on_windows():
    """
    Check if we're running on the Microsoft Windows OS.

    :returns: :data:`True` if running Windows, :data:`False` otherwise.
    """
    return sys.platform.startswith('win')

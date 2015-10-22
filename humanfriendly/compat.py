# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: October 22, 2015
# URL: https://humanfriendly.readthedocs.org

"""
Compatibility with Python 2 and 3.

This module exposes aliases and functions that make it easier to write Python
code that is compatible with Python 2 and Python 3.

.. data:: basestring

   Alias for :func:`python2:basestring` (in Python 2) or :class:`python3:str`
   (in Python 3). See also :func:`is_string()`.

.. data:: interactive_prompt

   Alias for :func:`python2:raw_input()` (in Python 2) or
   :func:`python3:input()` (in Python 3).

.. data:: StringIO

   Alias for :class:`python2:StringIO.StringIO` (in Python 2) or
   :class:`python3:io.StringIO` (in Python 3).

.. data:: unicode

   Alias for :func:`python2:unicode` (in Python 2) or :class:`python3:str` (in
   Python 3). See also :func:`coerce_string()`.
"""

try:
    # Python 2.
    unicode = unicode
    basestring = basestring
    interactive_prompt = raw_input  # NOQA
    from StringIO import StringIO
except (ImportError, NameError):
    # Python 3.
    unicode = str
    basestring = str
    interactive_prompt = input
    from io import StringIO  # NOQA


def coerce_string(value):
    """
    Coerce any value to a Unicode string (:func:`python2:unicode` in Python 2 and :class:`python3:str` in Python 3).

    :param value: The value to coerce.
    :returns: The value coerced to a Unicode string.
    """
    return value if is_string(value) else unicode(value)


def is_string(value):
    """
    Check whether a value is a :func:`python2:basestring` (in Python 2) or :class:`python2:str` (in Python 3).

    :param value: The value to check.
    :returns: :data:`True` if the value is a string, :data:`False` otherwise.
    """
    return isinstance(value, basestring)

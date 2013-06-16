# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: June 17, 2013
# URL: https://github.com/xolox/python-human-friendly

# Semi-standard module versioning.
__version__ = '1.2'

# Standard library modules.
import re
import os
import os.path

# Common disk size units, used for formatting and parsing.
disk_size_units = (dict(prefix='k', divider=1024**1, singular='KB', plural='KB'),
                   dict(prefix='m', divider=1024**2, singular='MB', plural='MB'),
                   dict(prefix='g', divider=1024**3, singular='GB', plural='GB'),
                   dict(prefix='t', divider=1024**4, singular='TB', plural='TB'),
                   dict(prefix='p', divider=1024**5, singular='PB', plural='PB'))

def format_size(nbytes, keep_width=False):
    """
    Format a byte count as a human readable file size
    (supports ranges from kilobytes to terabytes).

    :param nbytes: The size to format in bytes (an integer).
    :param keep_width: ``True`` if trailing zeros should not be stripped,
                       ``False`` if they can be stripped.
    :returns: The corresponding human readable file size (a string).
    """
    for unit in reversed(disk_size_units):
        if nbytes >= unit['divider']:
            count = round_size(float(nbytes) / unit['divider'], keep_width=keep_width)
            unit_label = unit['singular'] if count in ('1', '1.00') else unit['plural']
            return '%s %s' % (count, unit_label)
    return '%i %s' % (nbytes, 'byte' if nbytes == 1 else 'bytes')

def parse_size(size):
    """
    Parse a human readable data size and return the number of bytes. Raises
    :py:class:`InvalidSize` when the size cannot be parsed.

    :param size: The human readable file size to parse (a string).
    :returns: The corresponding size in bytes (an integer).
    """
    tokens = re.split(r'([0-9.]+)', size.lower())
    components = [s.strip() for s in tokens if s and not s.isspace()]
    if len(components) == 1 and components[0].isdigit():
        # If the string contains only an integer number, it is assumed to be
        # the number of bytes.
        return int(components[0])
    # Otherwise we expect to find two tokens: A number and a unit.
    if len(components) != 2:
        msg = "Expected to get two tokens, got %s!"
        raise InvalidSize, msg % components
    # Try to match the first letter of the unit.
    for unit in reversed(disk_size_units):
        if components[1].startswith(unit['prefix']):
            return int(float(components[0]) * unit['divider'])
    # Failed to match a unit: Explain what went wrong.
    msg = "Invalid disk size unit: %r"
    raise InvalidSize, msg % components[1]

def round_size(count, keep_width=False):
    """
    Helper for :py:func:`format_size()` to round a floating point number to two
    decimal places in a human friendly format: If no decimal places are
    required to represent the number, they will be omitted.

    :param nbytes: The disk size to format (a number).
    :param keep_width: ``True`` if trailing zeros should not be stripped,
                       ``False`` if they can be stripped.
    :returns: The formatted number as a string.
    """
    text = '%.2f' % float(count)
    if not keep_width:
        text = re.sub('0+$', '', text)
        text = re.sub('\.$', '', text)
    return text

def format_path(pathname):
    """
    Given an absolute pathname, abbreviate the user's home directory to ``~/``
    to shorten the pathname without losing information. It is not an error if
    the pathname is not relative to the current user's home directory.

    :param abspath: An absolute pathname.
    :returns: The pathname with the user's home directory abbreviated.
    """
    abspath = os.path.abspath(pathname)
    relpath = os.path.relpath(abspath, os.environ['HOME'])
    if relpath != abspath:
        relpath = os.path.join('~', relpath)
    return relpath

class InvalidSize(Exception):
    """
    Raised by :py:func:`parse_size()` when a string cannot be parsed into a
    file size.
    """
    pass

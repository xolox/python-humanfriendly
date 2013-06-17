# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: June 17, 2013
# URL: https://github.com/xolox/python-human-friendly

# Semi-standard module versioning.
__version__ = '1.3'

# Standard library modules.
import math
import os
import os.path
import re

# Common disk size units, used for formatting and parsing.
disk_size_units = (dict(prefix='k', divider=1024**1, singular='KB', plural='KB'),
                   dict(prefix='m', divider=1024**2, singular='MB', plural='MB'),
                   dict(prefix='g', divider=1024**3, singular='GB', plural='GB'),
                   dict(prefix='t', divider=1024**4, singular='TB', plural='TB'),
                   dict(prefix='p', divider=1024**5, singular='PB', plural='PB'))

# Common time units, used for formatting of time spans.
time_units = (dict(divider=1, singular='second', plural='seconds'),
              dict(divider=60, singular='minute', plural='minutes'),
              dict(divider=60*60, singular='hour', plural='hours'),
              dict(divider=60*60*24, singular='day', plural='days'),
              dict(divider=60*60*24*7, singular='week', plural='weeks'),
              dict(divider=60*60*24*7*52, singular='year', plural='years'))

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
            count = round_number(float(nbytes) / unit['divider'], keep_width=keep_width)
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

def round_number(count, keep_width=False):
    """
    Helper for :py:func:`format_size()` and :py:func:`format_timespan()` to
    round a floating point number to two decimal places in a human friendly
    format. If no decimal places are required to represent the number, they
    will be omitted.

    :param count: The number to format.
    :param keep_width: ``True`` if trailing zeros should not be stripped,
                       ``False`` if they can be stripped.
    :returns: The formatted number as a string.
    """
    text = '%.2f' % float(count)
    if not keep_width:
        text = re.sub('0+$', '', text)
        text = re.sub('\.$', '', text)
    return text

def format_timespan(seconds):
    """
    Format a timespan in seconds as a human readable string.

    :param seconds: Number of seconds (integer or float).
    :returns: The formatted timespan as a string.
    """
    if seconds < 60:
        # Fast path.
        unit_label = 'second' if math.floor(seconds) == 1 else 'seconds'
        return '%s %s' % (round_number(seconds, keep_width=False), unit_label)
    else:
        # Slow path.
        result = []
        for unit in reversed(time_units):
            if seconds >= unit['divider']:
                count = int(seconds / unit['divider'])
                seconds %= unit['divider']
                result.append('%i %s' % (count, unit['singular'] if count == 1 else unit['plural']))
        if len(result) == 1:
            # A single count/unit combination.
            return result[0]
        else:
            # Remove insignificant data from the formatted timespan.
            result = result[:3]
            # Multiple count/unit combinations.
            return ', '.join(result[:-1]) + ' and ' + result[-1]

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

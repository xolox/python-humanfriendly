# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: June 1, 2014
# URL: https://humanfriendly.readthedocs.org

# Semi-standard module versioning.
__version__ = '1.8.2'

# Standard library modules.
import math
import os
import os.path
import re
import sys
import time

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

def format_size(num_bytes, keep_width=False):
    """
    Format a byte count as a human readable file size (supports ranges from
    kilobytes to terabytes).

    :param num_bytes: The size to format in bytes (an integer).
    :param keep_width: ``True`` if trailing zeros should not be stripped,
                       ``False`` if they can be stripped.
    :returns: The corresponding human readable file size (a string).

    Some examples:

    >>> from humanfriendly import format_size
    >>> format_size(0)
    '0 bytes'
    >>> format_size(1)
    '1 byte'
    >>> format_size(5)
    '5 bytes'
    >>> format_size(1024 ** 2)
    '1 MB'
    >>> format_size(1024 ** 3 * 4)
    '4 GB'
    """
    for unit in reversed(disk_size_units):
        if num_bytes >= unit['divider']:
            number = round_number(float(num_bytes) / unit['divider'], keep_width=keep_width)
            return pluralize(number, unit['singular'], unit['plural'])
    return pluralize(num_bytes, 'byte', 'bytes')

def parse_size(size):
    """
    Parse a human readable data size and return the number of bytes. Raises
    :py:class:`InvalidSize` when the size cannot be parsed.

    :param size: The human readable file size to parse (a string).
    :returns: The corresponding size in bytes (an integer).

    Some examples:

    >>> from humanfriendly import parse_size
    >>> parse_size('42')
    42
    >>> parse_size('1 KB')
    1024
    >>> parse_size('5 kilobyte')
    5120
    >>> parse_size('1.5 GB')
    1610612736
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
        raise InvalidSize(msg % components)
    # Try to match the first letter of the unit.
    for unit in reversed(disk_size_units):
        if components[1].startswith(unit['prefix']):
            return int(float(components[0]) * unit['divider'])
    # Failed to match a unit: Explain what went wrong.
    msg = "Invalid disk size unit: %r"
    raise InvalidSize(msg % components[1])

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

    An example:

    >>> from humanfriendly import round_number
    >>> round_number(1)
    '1'
    >>> round_number(math.pi)
    '3.14'
    >>> round_number(5.001)
    '5'
    """
    text = '%.2f' % float(count)
    if not keep_width:
        text = re.sub('0+$', '', text)
        text = re.sub('\.$', '', text)
    return text

def format_timespan(num_seconds):
    """
    Format a timespan in seconds as a human readable string.

    :param num_seconds: Number of seconds (integer or float).
    :returns: The formatted timespan as a string.

    Some examples:

    >>> from humanfriendly import format_timespan
    >>> format_timespan(0)
    '0 seconds'
    >>> format_timespan(1)
    '1 second'
    >>> format_timespan(math.pi)
    '3.14 seconds'
    >>> hour = 60 * 60
    >>> day = hour * 24
    >>> week = day * 7
    >>> format_timespan(week * 52 + day * 2 + hour * 3)
    '1 year, 2 days and 3 hours'
    """
    if num_seconds < 60:
        # Fast path.
        return pluralize(round_number(num_seconds), 'second', 'seconds')
    else:
        # Slow path.
        result = []
        for unit in reversed(time_units):
            if num_seconds >= unit['divider']:
                count = int(num_seconds / unit['divider'])
                num_seconds %= unit['divider']
                result.append(pluralize(count, unit['singular'], unit['plural']))
        if len(result) == 1:
            # A single count/unit combination.
            return result[0]
        else:
            # Remove insignificant data from the formatted timespan and format
            # it in a readable way.
            return concatenate(result[:3])

def parse_date(datestring):
    """
    Parse a date string in one of the formats listed below. Raises
    :py:class:`InvalidDate` when the date cannot be parsed. Supported date/time
    formats:

    - ``YYYY-MM-DD``
    - ``YYYY-MM-DD HH:MM:SS``

    :param datestring: The date/time string to parse.
    :returns: A tuple with the numbers ``(year, month, day, hour, minute,
              second)`` (all numbers are integers).

    Examples:

    >>> from humanfriendly import parse_date
    >>> parse_date('2013-06-17')
    (2013, 6, 17, 0, 0, 0)
    >>> parse_date('2013-06-17 02:47:42')
    (2013, 6, 17, 2, 47, 42)

    Here's how you convert the result to a number:

    >>> from time import mktime
    >>> mktime(parse_date('2013-06-17 02:47:42') + (-1, -1, -1))
    1371430062.0

    And here's how you convert it to a :py:class:`datetime.datetime` object:

    >>> from datetime import datetime
    >>> datetime(*parse_date('2013-06-17 02:47:42'))
    datetime.datetime(2013, 6, 17, 2, 47, 42)
    """
    try:
        tokens = list(map(str.strip, datestring.split()))
        if len(tokens) >= 2:
            date_parts = list(map(int, tokens[0].split('-'))) + [1, 1]
            time_parts = list(map(int, tokens[1].split(':'))) + [0, 0, 0]
            return tuple(date_parts[0:3] + time_parts[0:3])
        else:
            year, month, day = (list(map(int, datestring.split('-'))) + [1, 1])[0:3]
            return (year, month, day, 0, 0, 0)
    except Exception:
        msg = "Invalid date! (expected 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' but got: %r)"
        raise InvalidDate(msg % datestring)

def format_path(pathname):
    """
    Given an absolute pathname, abbreviate the user's home directory to ``~/``
    in order to shorten the pathname without losing information. It is not an
    error if the pathname is not relative to the current user's home
    directory.

    :param pathname: An absolute pathname.
    :returns: The pathname with the user's home directory abbreviated.

    Here's an example of its usage:

    >>> from os import environ
    >>> from os.path import join
    >>> vimrc = join(environ['HOME'], '.vimrc')
    >>> vimrc
    '/home/peter/.vimrc'
    >>> from humanfriendly import format_path
    >>> format_path(vimrc)
    '~/.vimrc'
    """
    pathname = os.path.abspath(pathname)
    home = os.environ.get('HOME')
    if home:
        home = os.path.abspath(home)
        if pathname.startswith(home):
            pathname = os.path.join('~', os.path.relpath(pathname, home))
    return pathname

def pluralize(count, singular, plural):
    """
    Combine a count with the singular or plural form of a word.

    :param count: The count (a number).
    :param singular: The singular of the word.
    :param plural: The plural of the word.
    :returns: The count and applicable word in a string.
    """
    return '%s %s' % (count, singular if math.floor(float(count)) == 1 else plural)

def concatenate(items):
    """
    Concatenate a list of items in a human friendly way.

    :param items: A sequence of strings.
    :returns: A single string.
    """
    items = list(items)
    if len(items) > 1:
        return ', '.join(items[:-1]) + ' and ' + items[-1]
    elif items:
        return items[0]
    else:
        return ''

class Timer(object):

    """
    Easy to use timer to keep track of long during operations.
    """

    def __init__(self, start_time=None):
        """
        Remember the time when the :py:class:`Timer` was created.

        :param start_time: The start time (a float, defaults to the current time).
        """
        if start_time is None:
            start_time = time.time()
        self.start_time = start_time

    @property
    def elapsed_time(self):
        """
        Get the number of seconds elapsed since the :py:class:`Timer` was created.
        """
        return time.time() - self.start_time

    def __str__(self):
        """
        When a :py:class:`Timer` is coerced to a string it will show the
        elapsed time since the :py:class:`Timer` was created.
        """
        return format_timespan(self.elapsed_time)

class Spinner(object):

    """
    Show a "spinner" on the terminal to let the user know that something is
    happening during long running operations that would otherwise be silent.
    """

    def __init__(self, label, stream=sys.stderr):
        self.label = label
        self.stream = stream
        self.states = ['-', '\\', '|', '/']
        self.counter = 0
        self.last_update = 0
        try:
            self.interactive = stream.isatty()
        except Exception:
            self.interactive = False

    def step(self):
        """
        Advance the spinner by one step without starting a new line, causing
        an animated effect which is very simple but much nicer than waiting
        for a prompt which is completely silent for a long time.
        """
        if self.interactive:
            time_now = time.time()
            if time_now - self.last_update >= 0.2:
                self.last_update = time_now
                state = self.states[self.counter % len(self.states)]
                self.stream.write("\r %s %s " % (state, self.label))
                self.counter += 1

    def clear(self):
        """
        Clear the spinner. The next line which is shown on the standard
        output or error stream after calling this method will overwrite the
        line that used to show the spinner.
        """
        if self.interactive:
            self.stream.write("\r")

class InvalidSize(Exception):
    """
    Raised by :py:func:`parse_size()` when a string cannot be parsed into a
    file size:

    >>> from humanfriendly import parse_size
    >>> parse_size('5 Z')
    Traceback (most recent call last):
      File "humanfriendly.py", line 98, in parse_size
        raise InvalidSize, msg % components[1]
    humanfriendly.InvalidSize: Invalid disk size unit: 'z'
    """

class InvalidDate(Exception):
    """
    Raised by :py:func:`parse_date()` when a string cannot be parsed into a
    date:

    >>> from humanfriendly import parse_date
    >>> parse_date('2013-06-XY')
    Traceback (most recent call last):
      File "humanfriendly.py", line 206, in parse_date
        raise InvalidDate, msg % datestring
    humanfriendly.InvalidDate: Invalid date! (expected 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' but got: '2013-06-XY')
    """

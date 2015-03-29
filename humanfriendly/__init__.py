# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 29, 2015
# URL: https://humanfriendly.readthedocs.org

# Semi-standard module versioning.
__version__ = '1.16'

# Standard library modules.
import math
import multiprocessing
import os
import os.path
import re
import sys
import time

try:
    # Python 2.x.
    interactive_prompt = raw_input
    string_types = basestring
except NameError:
    # Python 3.x.
    interactive_prompt = input
    string_types = str

# Spinners are redrawn at most this many seconds.
minimum_spinner_interval = 0.2

# The following ANSI escape sequence can be used to clear a line and move the
# cursor back to the start of the line.
erase_line_code = '\r\x1b[K'

# Common disk size units, used for formatting and parsing.
disk_size_units = (dict(prefix='b', divider=1, singular='byte', plural='bytes'),
                   dict(prefix='k', divider=1024**1, singular='KB', plural='KB'),
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

def coerce_boolean(value):
    """
    Coerce any value to a boolean.

    :param value: Any Python value. If the value is a string:

                  - The strings '1', 'yes', 'true' and 'on' are coerced to ``True``.
                  - The strings '0', 'no', 'false' and 'off' are coerced to ``False``.
                  - Other strings raise an exception.

                  Other Python values are coerced using :py:func:`bool()`.
    :returns: A proper boolean value.
    :raises: :py:exc:`exceptions.ValueError` when the value is a string but
             cannot be coerced with certainty.
    """
    if isinstance(value, string_types):
        normalized = value.strip().lower()
        if normalized in ('1', 'yes', 'true', 'on'):
            return True
        elif normalized in ('0', 'no', 'false', 'off', ''):
            return False
        else:
            msg = "Failed to coerce string to boolean! (%r)"
            raise ValueError(msg % value)
    else:
        return bool(value)

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
    return pluralize(num_bytes, 'byte')

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
    '0.00 seconds'
    >>> format_timespan(1)
    '1.00 second'
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
        return pluralize(round_number(num_seconds), 'second')
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

    :param pathname: An absolute pathname (a string).
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

def parse_path(pathname):
    """
    Convert a human friendly pathname to an absolute pathname.

    Expands leading tildes using :py:func:`os.path.expanduser()` and
    environment variables using :py:func:`os.path.expandvars()` and makes the
    resulting pathname absolute using :py:func:`os.path.abspath()`.

    :param pathname: A human friendly pathname (a string).
    :returns: An absolute pathname (a string).
    """
    return os.path.abspath(os.path.expanduser(os.path.expandvars(pathname)))

def pluralize(count, singular, plural=None):
    """
    Combine a count with the singular or plural form of a word.

    If the plural form of the word is not provided it is obtained by
    concatenating the singular form of the word with the letter "s". Of course
    this will not always be correct, which is why you have the option to
    specify both forms.

    :param count: The count (a number).
    :param singular: The singular form of the word (a string).
    :param plural: The plural form of the word (a string or ``None``).
    :returns: The count and singular/plural word concatenated (a string).
    """
    if not plural:
        plural = singular + 's'
    return '%s %s' % (count, singular if math.floor(float(count)) == 1 else plural)

def concatenate(items):
    """
    Concatenate a list of items in a human friendly way.

    :param items: A sequence of strings.
    :returns: A single string.

    >>> from humanfriendly import concatenate
    >>> concatenate(["eggs", "milk", "bread"])
    'eggs, milk and bread'
    """
    items = list(items)
    if len(items) > 1:
        return ', '.join(items[:-1]) + ' and ' + items[-1]
    elif items:
        return items[0]
    else:
        return ''

def prompt_for_choice(choices, default=None):
    """
    Prompt the user to select a choice from a list of options.

    :param choices: A list of strings with available options.
    :param default: The default choice if the user simply presses Enter
                    (expected to be a string, defaults to ``None``).
    :returns: The string corresponding to the user's choice.
    """
    # By default the raw_input() prompt is very unfriendly, for example the
    # `Home' key enters `^[OH' and the `End' key enters `^[OF'. By simply
    # importing the `readline' module the prompt becomes much friendlier.
    import readline
    # Make sure we can use 'choices' more than once (i.e. not a generator).
    choices = list(choices)
    # Present the available choices in a user friendly way.
    for i, choice in enumerate(choices, start=1):
        text = u" %i. %s" % (i, choice)
        if choice == default:
            text += " (default choice)"
        print(text)
    # Loop until a valid choice is made.
    prompt = "Enter your choice as a number or unique substring (Ctrl-C aborts): "
    while True:
        input = interactive_prompt(prompt).strip()
        # Make sure the user entered something.
        if not input:
            if default is not None:
                return default
            continue
        # Check for a valid number.
        if input.isdigit():
            index = int(input) - 1
            if 0 <= index < len(choices):
                return choices[index]
        # Check for substring matches.
        matches = []
        for choice in choices:
            lower_input = input.lower()
            lower_choice = choice.lower()
            if lower_input == lower_choice:
                # If we have an 'exact' match we return it immediately.
                return choice
            elif lower_input in lower_choice:
                # Otherwise we gather substring matches.
                matches.append(choice)
        # If a single choice was matched we return it, otherwise we give the
        # user a hint about what went wrong.
        if len(matches) == 1:
            return matches[0]
        elif matches:
            print("Error: The string '%s' matches more than one choice (%s)." % (input, concatenate(matches)))
        elif input.isdigit():
            print("Error: The number %i is not a valid choice." % int(input))
        else:
            print("Error: The string '%s' doesn't match any choices." % input)

class Timer(object):

    """
    Easy to use timer to keep track of long during operations.
    """

    def __init__(self, start_time=None, resumable=False):
        """
        Remember the time when the :py:class:`Timer` was created.

        :param start_time: The start time (a float, defaults to the current time).
        :param resumable: Create a resumable timer (defaults to ``False``).
        """
        self.resumable = resumable
        if self.resumable:
            self.start_time = 0.0
            self.total_time = 0.0
        else:
            self.start_time = start_time or time.time()

    def __enter__(self):
        """
        Start or resume counting elapsed time.
        """
        if not self.resumable:
            raise ValueError("Timer is not resumable!")
        self.start_time = time.time()

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        """
        Stop counting elapsed time.
        """
        if not self.resumable:
            raise ValueError("Timer is not resumable!")
        self.total_time += time.time() - self.start_time
        self.start_time = 0

    @property
    def elapsed_time(self):
        """
        Get the number of seconds counted so far.
        """
        elapsed_time = 0
        if self.resumable:
            elapsed_time += self.total_time
        if self.start_time:
            elapsed_time += time.time() - self.start_time
        return elapsed_time

    @property
    def rounded(self):
        """Human readable timespan rounded to seconds (a string)."""
        return format_timespan(round(self.elapsed_time))

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

    >>> from time import sleep
    >>> from humanfriendly import Spinner
    >>> spin = Spinner(label="Downloading")
    >>> for i in xrange(100):
        sleep(0.1)
        spin.step()
    | Downloading  # cycles through | / - \\
    >>> spin = Spinner(label="Downloading", total=100)
    >>> for i in xrange(100):
        sleep(0.1)
        spin.step(i)
    | Downloading: 1.00% # travels up to 100%...

    If you want to provide user feedback during a long running operation but
    it's not practical to periodically call the :py:func:`~Spinner.step()`
    method consider using :py:class:`AutomaticSpinner` instead.
    """

    def __init__(self, label=None, total=0, stream=sys.stderr, interactive=None, timer=None):
        """
        Initialize a spinner.

        :param label: The label for the spinner (a string, defaults to ``None``).
        :param total: The expected number of steps (an integer).
        :param stream: The output stream to show the spinner on (defaults to
                       :py:data:`sys.stderr`).
        :param interactive: If this is ``False`` then the spinner doesn't write
                            to the output stream at all. It defaults to the
                            return value of ``stream.isatty()``.
        :param timer: A :py:class:`Timer` object (optional). If this is given
                      the spinner will show the elapsed time according to the
                      timer.
        """
        self.label = label
        self.total = total
        self.stream = stream
        self.states = ['-', '\\', '|', '/']
        self.counter = 0
        self.last_update = 0
        if interactive is None:
            # Try to automatically discover whether the stream is connected to
            # a terminal, but don't fail if no isatty() method is available.
            try:
                interactive = stream.isatty()
            except Exception:
                interactive = False
        self.interactive = interactive
        self.timer = timer

    def step(self, progress=0, label=None):
        """
        Advance the spinner by one step without starting a new line, causing
        an animated effect which is very simple but much nicer than waiting
        for a prompt which is completely silent for a long time. Progress
        should be the amount out of ``Spinner.total`` that is complete, not
        a step amount.
        """
        if self.interactive:
            time_now = time.time()
            if time_now - self.last_update >= minimum_spinner_interval:
                self.last_update = time_now
                state = self.states[self.counter % len(self.states)]
                label = label or self.label
                if not label:
                    raise Exception("No label set for spinner!")
                elif self.total and progress:
                    label = "%s: %.2f%%" % (label, progress/(self.total/100.0))
                elif self.timer and self.timer.elapsed_time > 2:
                    label = "%s (%s)" % (label, self.timer.rounded)
                self.stream.write("%s %s %s .. " % (erase_line_code, state, label))
                self.counter += 1

    def clear(self):
        """
        Clear the spinner. The next line which is shown on the standard
        output or error stream after calling this method will overwrite the
        line that used to show the spinner.
        """
        if self.interactive:
            self.stream.write(erase_line_code)

class AutomaticSpinner(object):

    """
    Show a "spinner" on the terminal (just like :py:class:`Spinner` does) that
    automatically starts animating. This class should be used as a context
    manager using the :py:keyword:`with` statement. The animation continues for
    as long as the context is active.

    :py:class:`AutomaticSpinner` provides an alternative to :py:class:`Spinner`
    for situations where it is not practical for the caller to periodically
    call :py:func:`~Spinner.step()` to advance the animation, e.g. because
    you're performing a blocking call and don't fancy implementing threading or
    subprocess handling just to provide some user feedback.

    This works using the :py:mod:`multiprocessing` module by spawning a
    subprocess to render the spinner while the main process is busy doing
    something more useful. By using the :py:keyword:`with` statement you're
    guaranteed that the subprocess is properly terminated at the appropriate
    time.
    """

    def __init__(self, label, show_time=True):
        """
        Initialize an automatic spinner.

        :param label: The label for the spinner (a string).
        :param show_time: If this is ``True`` (the default) then the spinner
                          shows elapsed time.
        """
        self.shutdown_event = multiprocessing.Event()
        self.subprocess = multiprocessing.Process(target=automatic_spinner_target,
                                                  args=(label, show_time, self.shutdown_event))

    def __enter__(self):
        self.subprocess.start()

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.shutdown_event.set()
        self.subprocess.join()
        sys.stderr.write(erase_line_code)

def automatic_spinner_target(label, show_time, shutdown_event):
    try:
        timer = Timer() if show_time else None
        spinner = Spinner(label=label, stream=sys.stderr, timer=timer)
        while not shutdown_event.is_set():
            spinner.step()
            time.sleep(minimum_spinner_interval)
    except KeyboardInterrupt:
        # Swallow Control-C signals without producing a nasty traceback that
        # won't make any sense to the average user.
        pass

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

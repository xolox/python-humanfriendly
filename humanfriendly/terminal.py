# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: February 17, 2016
# URL: https://humanfriendly.readthedocs.org

"""
Interaction with UNIX terminals.

The :mod:`~humanfriendly.terminal` module makes it easy to interact with UNIX
terminals and format text for rendering on UNIX terminals. If the terms used in
the documentation of this module don't make sense to you then please refer to
the `Wikipedia article on ANSI escape sequences`_ for details about how ANSI
escape sequences work.

.. _Wikipedia article on ANSI escape sequences: http://en.wikipedia.org/wiki/ANSI_escape_code#Sequence_elements
"""

# Standard library modules.
import os
import re
import subprocess
import sys

# The `fcntl' module is platform specific so importing it may give an error. We
# hide this implementation detail from callers by handling the import error and
# setting a flag instead.
try:
    import fcntl
    import termios
    import struct
    HAVE_IOCTL = True
except ImportError:
    HAVE_IOCTL = False

# Modules included in our package. We import find_meta_variables() here to
# preserve backwards compatibility with older versions of humanfriendly where
# that function was defined in this module.
from humanfriendly.text import concatenate, format
from humanfriendly.usage import find_meta_variables, format_usage  # NOQA

ANSI_CSI = '\x1b['
"""The ANSI "Control Sequence Introducer" (a string)."""

ANSI_SGR = 'm'
"""The ANSI "Select Graphic Rendition" sequence (a string)."""

ANSI_ERASE_LINE = '%sK' % ANSI_CSI
"""The ANSI escape sequence to erase the current line (a string)."""

ANSI_RESET = '%s0%s' % (ANSI_CSI, ANSI_SGR)
"""The ANSI escape sequence to reset styling (a string)."""

ANSI_COLOR_CODES = dict(black=0, red=1, green=2, yellow=3, blue=4, magenta=5, cyan=6, white=7)
"""
A dictionary with (name, number) pairs of `portable color codes`_. Used by
:func:`ansi_style()` to generate ANSI escape sequences that change font color.

.. _portable color codes: http://en.wikipedia.org/wiki/ANSI_escape_code#Colors
"""

ANSI_TEXT_STYLES = dict(bold=1, faint=2, underline=4, inverse=7, strike_through=9)
"""
A dictionary with (name, number) pairs of text styles (effects). Used by
:func:`ansi_style()` to generate ANSI escape sequences that change text
styles. Only widely supported text styles are included here.
"""

DEFAULT_LINES = 25
"""The default number of lines in a terminal (an integer)."""

DEFAULT_COLUMNS = 80
"""The default number of columns in a terminal (an integer)."""

HIGHLIGHT_COLOR = os.environ.get('HUMANFRIENDLY_HIGHLIGHT_COLOR', 'green')
"""
The color used to highlight important tokens in formatted text (e.g. the usage
message of the ``humanfriendly`` program). If the environment variable
``$HUMANFRIENDLY_HIGHLIGHT_COLOR`` is set it determines the value of
:data:`HIGHLIGHT_COLOR`.
"""


def message(*args, **kw):
    """
    Show an informational message on the terminal.

    :param args: Any position arguments are passed on to :func:`~humanfriendly.text.format()`.
    :param kw: Any keyword arguments are passed on to :func:`~humanfriendly.text.format()`.

    Renders the message using :func:`~humanfriendly.text.format()` and writes
    the resulting string to :data:`sys.stderr` (followed by a newline).
    """
    sys.stderr.write(format(*args, **kw) + '\n')


def warning(*args, **kw):
    """
    Show a warning message on the terminal.

    :param args: Any position arguments are passed on to :func:`~humanfriendly.text.format()`.
    :param kw: Any keyword arguments are passed on to :func:`~humanfriendly.text.format()`.

    Renders the message using :func:`~humanfriendly.text.format()` and writes
    the resulting string to :data:`sys.stderr` (followed by a newline). If
    :data:`sys.stderr` is connected to a terminal :func:`ansi_wrap()` is used
    to color the message in a red font (to make the warning stand out from
    surrounding text).
    """
    text = format(*args, **kw)
    if terminal_supports_colors(sys.stderr):
        text = ansi_wrap(text, color='red')
    sys.stderr.write(text + '\n')


def ansi_strip(text, readline_hints=True):
    """
    Strip ANSI escape sequences from the given string.

    :param text: The text from which ANSI escape sequences should be removed (a
                 string).
    :param readline_hints: If :data:`True` then :func:`readline_strip()` is
                           used to remove `readline hints`_ from the string.
    :returns: The text without ANSI escape sequences (a string).
    """
    pattern = '%s.*?%s' % (re.escape(ANSI_CSI), re.escape(ANSI_SGR))
    text = re.sub(pattern, '', text)
    if readline_hints:
        text = readline_strip(text)
    return text


def ansi_style(**kw):
    """
    Generate ANSI escape sequences for the given color and/or style(s).

    :param color: The name of a color (one of the strings 'black', 'red',
                  'green', 'yellow', 'blue', 'magenta', 'cyan' or 'white') or
                  :data:`None` (the default) which means no escape sequence to
                  switch color will be emitted.
    :param readline_hints: If :data:`True` then :func:`readline_wrap()` is
                           applied to the generated ANSI escape sequences (the
                           default is :data:`False`).
    :param kw: Any additional keyword arguments are expected to match an entry
               in the :data:`ANSI_TEXT_STYLES` dictionary. If the argument's
               value evaluates to :data:`True` the respective style will be
               enabled.
    :returns: The ANSI escape sequences to enable the requested text styles or
              an empty string if no styles were requested.
    :raises: :py:exc:`~exceptions.ValueError` when an invalid color name is given.
    """
    # Start with sequences that change text styles.
    sequences = [str(ANSI_TEXT_STYLES[k]) for k, v in kw.items() if k in ANSI_TEXT_STYLES and v]
    # Append the color code (if any).
    color_name = kw.get('color')
    if color_name:
        # Validate the color name.
        if color_name not in ANSI_COLOR_CODES:
            msg = "Invalid color name %r! (expected one of %s)"
            raise ValueError(msg % (color_name, concatenate(sorted(ANSI_COLOR_CODES))))
        sequences.append('3%i' % ANSI_COLOR_CODES[color_name])
    if sequences:
        encoded = ANSI_CSI + ';'.join(sequences) + ANSI_SGR
        return readline_wrap(encoded) if kw.get('readline_hints') else encoded
    else:
        return ''


def ansi_width(text):
    """
    Calculate the effective width of the given text (ignoring ANSI escape sequences).

    :param text: The text whose width should be calculated (a string).
    :returns: The width of the text without ANSI escape sequences (an
              integer).

    This function uses :func:`ansi_strip()` to strip ANSI escape sequences from
    the given string and returns the length of the resulting string.
    """
    return len(ansi_strip(text))


def ansi_wrap(text, **kw):
    """
    Wrap text in ANSI escape sequences for the given color and/or style(s).

    :param text: The text to wrap (a string).
    :param kw: Any keyword arguments are passed to :func:`ansi_style()`.
    :returns: The result of this function depends on the keyword arguments:

              - If :func:`ansi_style()` generates an ANSI escape sequence based
                on the keyword arguments, the given text is prefixed with the
                generated ANSI escape sequence and suffixed with
                :data:`ANSI_RESET`.

              - If :func:`ansi_style()` returns an empty string then the text
                given by the caller is returned unchanged.
    """
    start_sequence = ansi_style(**kw)
    if start_sequence:
        end_sequence = ANSI_RESET
        if kw.get('readline_hints'):
            end_sequence = readline_wrap(end_sequence)
        return start_sequence + text + end_sequence
    else:
        return text


def readline_wrap(expr):
    """
    Wrap an ANSI escape sequence in `readline hints`_.

    :param text: The text with the escape sequence to wrap (a string).
    :returns: The wrapped text.

    .. _readline hints: http://superuser.com/a/301355
    """
    return '\001' + expr + '\002'


def readline_strip(expr):
    """
    Remove `readline hints`_ from a string.

    :param text: The text to strip (a string).
    :returns: The stripped text.
    """
    return expr.replace('\001', '').replace('\002', '')


def connected_to_terminal(stream=None):
    """
    Check if a stream is connected to a terminal.

    :param stream: The stream to check (a file-like object,
                   defaults to :data:`sys.stdout`).
    :returns: :data:`True` if the stream is connected to a terminal,
              :data:`False` otherwise.

    See also :func:`terminal_supports_colors()`.
    """
    stream = sys.stdout if stream is None else stream
    try:
        return stream.isatty()
    except Exception:
        return False


def terminal_supports_colors(stream=None):
    """
    Check if a stream is connected to a terminal that supports ANSI escape sequences.

    :param stream: The stream to check (a file-like object,
                   defaults to :data:`sys.stdout`).
    :returns: :data:`True` if the terminal supports ANSI escape sequences,
              :data:`False` otherwise.

    This function is inspired by the implementation of
    `django.core.management.color.supports_color()
    <https://github.com/django/django/blob/master/django/core/management/color.py>`_.
    """
    return (sys.platform != 'Pocket PC' and
            (sys.platform != 'win32' or 'ANSICON' in os.environ) and
            connected_to_terminal(stream))


def find_terminal_size():
    """
    Determine the number of lines and columns visible in the terminal.

    :returns: A tuple of two integers with the line and column count.

    The result of this function is based on the first of the following three
    methods that works:

    1. First :func:`find_terminal_size_using_ioctl()` is tried,
    2. then :func:`find_terminal_size_using_stty()` is tried,
    3. finally :data:`DEFAULT_LINES` and :data:`DEFAULT_COLUMNS` are returned.

    .. note:: The :func:`find_terminal_size()` function performs the steps
              above every time it is called, the result is not cached. This is
              because the size of a virtual terminal can change at any time and
              the result of :func:`find_terminal_size()` should be correct.

              `Pre-emptive snarky comment`_: It's possible to cache the result
              of this function and use :data:`signal.SIGWINCH` to refresh the
              cached values!

              Response: As a library I don't consider it the role of the
              :py:mod:`humanfriendly.terminal` module to install a process wide
              signal handler ...

    .. _Pre-emptive snarky comment: http://blogs.msdn.com/b/oldnewthing/archive/2008/01/30/7315957.aspx
    """
    # The first method. Any of the standard streams may have been redirected
    # somewhere and there's no telling which, so we'll just try them all.
    for stream in sys.stdin, sys.stdout, sys.stderr:
        try:
            result = find_terminal_size_using_ioctl(stream)
            if min(result) >= 1:
                return result
        except Exception:
            pass
    # The second method.
    try:
        result = find_terminal_size_using_stty()
        if min(result) >= 1:
            return result
    except Exception:
        pass
    # Fall back to conservative defaults.
    return DEFAULT_LINES, DEFAULT_COLUMNS


def find_terminal_size_using_ioctl(stream):
    """
    Find the terminal size using :func:`fcntl.ioctl()`.

    :param stream: A stream connected to the terminal (a file object with a
                   ``fileno`` attribute).
    :returns: A tuple of two integers with the line and column count.
    :raises: This function can raise exceptions but I'm not going to document
             them here, you should be using :func:`find_terminal_size()`.

    Based on an `implementation found on StackOverflow <http://stackoverflow.com/a/3010495/788200>`_.
    """
    if not HAVE_IOCTL:
        raise NotImplementedError("It looks like the `fcntl' module is not available!")
    h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(stream, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
    return h, w


def find_terminal_size_using_stty():
    """
    Find the terminal size using the external command ``stty size``.

    :param stream: A stream connected to the terminal (a file object).
    :returns: A tuple of two integers with the line and column count.
    :raises: This function can raise exceptions but I'm not going to document
             them here, you should be using :func:`find_terminal_size()`.
    """
    stty = subprocess.Popen(['stty', 'size'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = stty.communicate()
    tokens = stdout.split()
    if len(tokens) != 2:
        raise Exception("Invalid output from `stty size'!")
    return tuple(map(int, tokens))


def usage(usage_text):
    """
    Print a human friendly usage message to the terminal.

    :param text: The usage message to print (a string).

    This function does two things:

    1. If :data:`sys.stdout` is connected to a terminal (see
       :func:`connected_to_terminal()`) then the usage message is formatted
       using :func:`.format_usage()`.
    2. The usage message is shown using a pager (see :func:`show_pager()`).
    """
    if terminal_supports_colors(sys.stdout):
        usage_text = format_usage(usage_text)
    show_pager(usage_text)


def show_pager(formatted_text):
    """
    Print a large text to the terminal using a pager.

    :param formatted_text: The text to print to the terminal (a string).

    The use of a pager helps to avoid the wall of text effect where the user
    has to scroll up to see where the output began (not very user friendly).

    If :data:`sys.stdout` is not connected to a terminal (see
    :func:`connected_to_terminal()`) then the text is printed directly without
    invoking a pager.

    If the given text contains ANSI escape sequences the command ``less
    --RAW-CONTROL-CHARS`` is used, otherwise ``$PAGER`` is used (if ``$PAGER``
    isn't set the command ``less`` is used).
    """
    if connected_to_terminal(sys.stdout):
        if ANSI_CSI in formatted_text:
            pager_command = ['less', '--RAW-CONTROL-CHARS']
        else:
            pager_command = [os.environ.get('PAGER', 'less')]
        pager = subprocess.Popen(pager_command, stdin=subprocess.PIPE)
        pager.communicate(input=formatted_text)
    else:
        print(formatted_text)

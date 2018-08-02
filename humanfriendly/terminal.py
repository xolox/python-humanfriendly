# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: August 2, 2018
# URL: https://humanfriendly.readthedocs.io

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
import codecs
import numbers
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
from humanfriendly.compat import HTMLParser, StringIO, coerce_string, name2codepoint, is_unicode, unichr
from humanfriendly.text import compact_empty_lines, concatenate, format
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

ANSI_TEXT_STYLES = dict(bold=1, faint=2, italic=3, underline=4, inverse=7, strike_through=9)
"""
A dictionary with (name, number) pairs of text styles (effects). Used by
:func:`ansi_style()` to generate ANSI escape sequences that change text
styles. Only widely supported text styles are included here.
"""

CLEAN_OUTPUT_PATTERN = re.compile(u'(\r|\n|\b|%s)' % re.escape(ANSI_ERASE_LINE))
"""
A compiled regular expression used to separate significant characters from other text.

This pattern is used by :func:`clean_terminal_output()` to split terminal
output into regular text versus backspace, carriage return and line feed
characters and ANSI 'erase line' escape sequences.
"""

DEFAULT_LINES = 25
"""The default number of lines in a terminal (an integer)."""

DEFAULT_COLUMNS = 80
"""The default number of columns in a terminal (an integer)."""

DEFAULT_ENCODING = 'UTF-8'
"""The output encoding for Unicode strings."""

HIGHLIGHT_COLOR = os.environ.get('HUMANFRIENDLY_HIGHLIGHT_COLOR', 'green')
"""
The color used to highlight important tokens in formatted text (e.g. the usage
message of the ``humanfriendly`` program). If the environment variable
``$HUMANFRIENDLY_HIGHLIGHT_COLOR`` is set it determines the value of
:data:`HIGHLIGHT_COLOR`.
"""


def output(text, *args, **kw):
    """
    Print a formatted message to the standard output stream.

    For details about argument handling please refer to
    :func:`~humanfriendly.text.format()`.

    Renders the message using :func:`~humanfriendly.text.format()` and writes
    the resulting string (followed by a newline) to :data:`sys.stdout` using
    :func:`auto_encode()`.
    """
    auto_encode(sys.stdout, coerce_string(text) + '\n', *args, **kw)


def message(text, *args, **kw):
    """
    Print a formatted message to the standard error stream.

    For details about argument handling please refer to
    :func:`~humanfriendly.text.format()`.

    Renders the message using :func:`~humanfriendly.text.format()` and writes
    the resulting string (followed by a newline) to :data:`sys.stderr` using
    :func:`auto_encode()`.
    """
    auto_encode(sys.stderr, coerce_string(text) + '\n', *args, **kw)


def warning(text, *args, **kw):
    """
    Show a warning message on the terminal.

    For details about argument handling please refer to
    :func:`~humanfriendly.text.format()`.

    Renders the message using :func:`~humanfriendly.text.format()` and writes
    the resulting string (followed by a newline) to :data:`sys.stderr` using
    :func:`auto_encode()`.

    If :data:`sys.stderr` is connected to a terminal that supports colors,
    :func:`ansi_wrap()` is used to color the message in a red font (to make
    the warning stand out from surrounding text).
    """
    text = coerce_string(text)
    if terminal_supports_colors(sys.stderr):
        text = ansi_wrap(text, color='red')
    auto_encode(sys.stderr, text + '\n', *args, **kw)


def auto_encode(stream, text, *args, **kw):
    """
    Reliably write Unicode strings to the terminal.

    :param stream: The file-like object to write to (a value like
                   :data:`sys.stdout` or :data:`sys.stderr`).
    :param text: The text to write to the stream (a string).
    :param args: Refer to :func:`~humanfriendly.text.format()`.
    :param kw: Refer to :func:`~humanfriendly.text.format()`.

    Renders the text using :func:`~humanfriendly.text.format()` and writes it
    to the given stream. If an :exc:`~exceptions.UnicodeEncodeError` is
    encountered in doing so, the text is encoded using :data:`DEFAULT_ENCODING`
    and the write is retried. The reasoning behind this rather blunt approach
    is that it's preferable to get output on the command line in the wrong
    encoding then to have the Python program blow up with a
    :exc:`~exceptions.UnicodeEncodeError` exception.
    """
    text = format(text, *args, **kw)
    try:
        stream.write(text)
    except UnicodeEncodeError:
        stream.write(codecs.encode(text, DEFAULT_ENCODING))


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

    :param color: The foreground color. Three types of values are supported:

                  - The name of a color (one of the strings 'black', 'red',
                    'green', 'yellow', 'blue', 'magenta', 'cyan' or 'white').
                  - An integer that refers to the 256 color mode palette.
                  - A tuple or list with three integers representing an RGB
                    (red, green, blue) value.

                  The value :data:`None` (the default) means no escape
                  sequence to switch color will be emitted.
    :param background: The background color (see the description
                       of the `color` argument).
    :param bright: Use high intensity colors instead of default colors
                   (a boolean, defaults to :data:`False`).
    :param readline_hints: If :data:`True` then :func:`readline_wrap()` is
                           applied to the generated ANSI escape sequences (the
                           default is :data:`False`).
    :param kw: Any additional keyword arguments are expected to match a key
               in the :data:`ANSI_TEXT_STYLES` dictionary. If the argument's
               value evaluates to :data:`True` the respective style will be
               enabled.
    :returns: The ANSI escape sequences to enable the requested text styles or
              an empty string if no styles were requested.
    :raises: :exc:`~exceptions.ValueError` when an invalid color name is given.

    Even though only eight named colors are supported, the use of `bright=True`
    and `faint=True` increases the number of available colors to around 24 (it
    may be slightly lower, for example because faint black is just black).

    **Support for 8-bit colors**

    In `release 4.7`_ support for 256 color mode was added. While this
    significantly increases the available colors it's not very human friendly
    in usage because you need to look up color codes in the `256 color mode
    palette <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_.

    You can use the ``humanfriendly --demo`` command to get a demonstration of
    the available colors, see also the screen shot below. Note that the small
    font size in the screen shot was so that the demonstration of 256 color
    mode support would fit into a single screen shot without scrolling :-)
    (I wasn't feeling very creative).

      .. image:: images/ansi-demo.png

    **Support for 24-bit colors**

    In `release 4.14`_ support for 24-bit colors was added by accepting a tuple
    or list with three integers representing the RGB (red, green, blue) value
    of a color. This is not included in the demo because rendering millions of
    colors was deemed unpractical ;-).

    .. _release 4.7: http://humanfriendly.readthedocs.io/en/latest/changelog.html#release-4-7-2018-01-14
    .. _release 4.14: http://humanfriendly.readthedocs.io/en/latest/changelog.html#release-4-14-2018-07-13
    """
    # Start with sequences that change text styles.
    sequences = [ANSI_TEXT_STYLES[k] for k, v in kw.items() if k in ANSI_TEXT_STYLES and v]
    # Append the color code (if any).
    for color_type in 'color', 'background':
        color_value = kw.get(color_type)
        if isinstance(color_value, (tuple, list)):
            if len(color_value) != 3:
                msg = "Invalid color value %r! (expected tuple or list with three numbers)"
                raise ValueError(msg % color_value)
            sequences.append(48 if color_type == 'background' else 38)
            sequences.append(2)
            sequences.extend(map(int, color_value))
        elif isinstance(color_value, numbers.Number):
            # Numeric values are assumed to be 256 color codes.
            sequences.extend((
                39 if color_type == 'background' else 38,
                5, int(color_value)
            ))
        elif color_value:
            # Other values are assumed to be strings containing one of the known color names.
            if color_value not in ANSI_COLOR_CODES:
                msg = "Invalid color value %r! (expected an integer or one of the strings %s)"
                raise ValueError(msg % (color_value, concatenate(map(repr, sorted(ANSI_COLOR_CODES)))))
            # Pick the right offset for foreground versus background
            # colors and regular intensity versus bright colors.
            offset = (
                (100 if kw.get('bright') else 40)
                if color_type == 'background'
                else (90 if kw.get('bright') else 30)
            )
            # Combine the offset and color code into a single integer.
            sequences.append(offset + ANSI_COLOR_CODES[color_value])
    if sequences:
        encoded = ANSI_CSI + ';'.join(map(str, sequences)) + ANSI_SGR
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


def clean_terminal_output(text):
    """
    Clean up the terminal output of a command.

    :param text: The raw text with special characters (a Unicode string).
    :returns: A list of Unicode strings (one for each line).

    This function emulates the effect of backspace (0x08), carriage return
    (0x0D) and line feed (0x0A) characters and the ANSI 'erase line' escape
    sequence on interactive terminals. It's intended to clean up command output
    that was originally meant to be rendered on an interactive terminal and
    that has been captured using e.g. the script_ program [#]_ or the
    :mod:`pty` module [#]_.

    .. [#] My coloredlogs_ package supports the ``coloredlogs --to-html``
           command which uses script_ to fool a subprocess into thinking that
           it's connected to an interactive terminal (in order to get it to
           emit ANSI escape sequences).

    .. [#] My capturer_ package uses the :mod:`pty` module to fool the current
           process and subprocesses into thinking they are connected to an
           interactive terminal (in order to get them to emit ANSI escape
           sequences).

    **Some caveats about the use of this function:**

    - Strictly speaking the effect of carriage returns cannot be emulated
      outside of an actual terminal due to the interaction between overlapping
      output, terminal widths and line wrapping. The goal of this function is
      to sanitize noise in terminal output while preserving useful output.
      Think of it as a useful and pragmatic but possibly lossy conversion.

    - The algorithm isn't smart enough to properly handle a pair of ANSI escape
      sequences that open before a carriage return and close after the last
      carriage return in a linefeed delimited string; the resulting string will
      contain only the closing end of the ANSI escape sequence pair. Tracking
      this kind of complexity requires a state machine and proper parsing.

    .. _capturer: https://pypi.python.org/pypi/capturer
    .. _coloredlogs: https://pypi.python.org/pypi/coloredlogs
    .. _script: http://man7.org/linux/man-pages/man1/script.1.html
    """
    cleaned_lines = []
    current_line = ''
    current_position = 0
    for token in CLEAN_OUTPUT_PATTERN.split(text):
        if token == '\r':
            # Seek back to the start of the current line.
            current_position = 0
        elif token == '\b':
            # Seek back one character in the current line.
            current_position = max(0, current_position - 1)
        else:
            if token == '\n':
                # Capture the current line.
                cleaned_lines.append(current_line)
            if token in ('\n', ANSI_ERASE_LINE):
                # Clear the current line.
                current_line = ''
                current_position = 0
            elif token:
                # Merge regular output into the current line.
                new_position = current_position + len(token)
                prefix = current_line[:current_position]
                suffix = current_line[new_position:]
                current_line = prefix + token + suffix
                current_position = new_position
    # Capture the last line (if any).
    cleaned_lines.append(current_line)
    # Remove any empty trailing lines.
    while cleaned_lines and not cleaned_lines[-1]:
        cleaned_lines.pop(-1)
    return cleaned_lines


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


def html_to_ansi(data, callback=None):
    """
    Convert HTML with simple text formatting to text with ANSI escape sequences.

    :param data: The HTML to convert (a string).
    :param callback: Optional callback to pass to :class:`HTMLConverter`.
    :returns: Text with ANSI escape sequences (a string).

    Please refer to the documentation of the :class:`HTMLConverter` class for
    details about the conversion process (like which tags are supported) and an
    example with a screenshot.
    """
    converter = HTMLConverter(callback=callback)
    return converter(data)


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
              :mod:`humanfriendly.terminal` module to install a process wide
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


def show_pager(formatted_text, encoding=DEFAULT_ENCODING):
    """
    Print a large text to the terminal using a pager.

    :param formatted_text: The text to print to the terminal (a string).
    :param encoding: The name of the text encoding used to encode the formatted
                     text if the formatted text is a Unicode string (a string,
                     defaults to :data:`DEFAULT_ENCODING`).

    When :func:`connected_to_terminal()` returns :data:`True` a pager is used
    to show the text on the terminal, otherwise the text is printed directly
    without invoking a pager.

    The use of a pager helps to avoid the wall of text effect where the user
    has to scroll up to see where the output began (not very user friendly).

    Refer to :func:`get_pager_command()` for details about the command line
    that's used to invoke the pager.
    """
    if connected_to_terminal():
        command_line = get_pager_command(formatted_text)
        pager = subprocess.Popen(command_line, stdin=subprocess.PIPE)
        if is_unicode(formatted_text):
            formatted_text = formatted_text.encode(encoding)
        pager.communicate(input=formatted_text)
    else:
        output(formatted_text)


def get_pager_command(text=None):
    """
    Get the command to show a text on the terminal using a pager.

    :param text: The text to print to the terminal (a string).
    :returns: A list of strings with the pager command and arguments.

    The use of a pager helps to avoid the wall of text effect where the user
    has to scroll up to see where the output began (not very user friendly).

    If the given text contains ANSI escape sequences the command ``less
    --RAW-CONTROL-CHARS`` is used, otherwise the environment variable
    ``$PAGER`` is used (if ``$PAGER`` isn't set less_ is used).

    When the selected pager is less_, the following options are used to make
    the experience more user friendly:

    - ``--quit-if-one-screen`` causes less_ to automatically exit if the entire
      text can be displayed on the first screen. This makes the use of a pager
      transparent for smaller texts (because the operator doesn't have to quit
      the pager).

    - ``--no-init`` prevents less_ from clearing the screen when it exits. This
      ensures that the operator gets a chance to review the text (for example a
      usage message) after quitting the pager, while composing the next command.

    .. _less: http://man7.org/linux/man-pages/man1/less.1.html
    """
    # Compose the pager command.
    if text and ANSI_CSI in text:
        command_line = ['less', '--RAW-CONTROL-CHARS']
    else:
        command_line = [os.environ.get('PAGER', 'less')]
    # Pass some additional options to `less' (to make it more
    # user friendly) without breaking support for other pagers.
    if os.path.basename(command_line[0]) == 'less':
        command_line.append('--no-init')
        command_line.append('--quit-if-one-screen')
    return command_line


class HTMLConverter(HTMLParser):

    """
    Convert HTML with simple text formatting to text with ANSI escape sequences.

    The following text styles are supported:

    - Bold: ``<b>``, ``<strong>`` and ``<span style="font-weight: bold;">``
    - Italic: ``<i>``, ``<em>`` and ``<span style="font-style: italic;">``
    - Strike-through: ``<del>``, ``<s>`` and ``<span style="text-decoration: line-through;">``
    - Underline: ``<ins>``, ``<u>`` and ``<span style="text-decoration: underline">``

    Colors can be specified as follows:

    - Foreground color: ``<span style="color: #RRGGBB;">``
    - Background color: ``<span style="background-color: #RRGGBB;">``

    Here's a small demonstration:

    .. code-block:: python

       from humanfriendly.text import dedent
       from humanfriendly.terminal import html_to_ansi

       print(html_to_ansi(dedent('''
         <b>Hello world!</b>
         <i>Is this thing on?</i>
         I guess I can <u>underline</u> or <s>strike-through</s> text?
         And what about <span style="color: red">color</span>?
       ''')))

       rainbow_colors = [
           '#FF0000', '#E2571E', '#FF7F00', '#FFFF00', '#00FF00',
           '#96BF33', '#0000FF', '#4B0082', '#8B00FF', '#FFFFFF',
       ]
       html_rainbow = "".join('<span style="color: %s">o</span>' % c for c in rainbow_colors)
       print(html_to_ansi("Let's try a rainbow: %s" % html_rainbow))

    Here's what the results look like:

      .. image:: images/html-to-ansi.png

    Some more details:

    - Nested tags are supported, within reasonable limits.

    - Text in ``<code>`` and ``<pre>`` tags will be highlighted in a
      different color from the main text (currently this is yellow).

    - ``<a href="URL">TEXT</a>`` is converted to the format "TEXT (URL)" where
      the uppercase symbols are highlighted in light blue with an underline.

    - ``<div>``, ``<p>`` and ``<pre>`` tags are considered block level tags
      and are wrapped in vertical whitespace to prevent their content from
      "running into" surrounding text. This may cause runs of multiple empty
      lines to be emitted. As a *workaround* the :func:`__call__()` method
      will automatically call :func:`.compact_empty_lines()` on the generated
      output before returning it to the caller. Of course this won't work
      when `output` is set to something like :data:`sys.stdout`.

    - ``<br>`` is converted to a single plain text line break.

    Implementation notes:

    - A list of dictionaries with style information is used as a stack where
      new styling can be pushed and a pop will restore the previous styling.
      When new styling is pushed, it is merged with (but overrides) the current
      styling.

    - If you're going to be converting a lot of HTML it might be useful from
      a performance standpoint to re-use an existing :class:`HTMLConverter`
      object for unrelated HTML fragments, in this case take a look at the
      :func:`__call__()` method (it makes this use case very easy).

    .. versionadded:: 4.15
       :class:`humanfriendly.terminal.HTMLConverter` was added to the
       `humanfriendly` package during the initial development of my new
       `chat-archive <https://chat-archive.readthedocs.io/>`_ project, whose
       command line interface makes for a great demonstration of the
       flexibility that this feature provides (hint: check out how the search
       keyword highlighting combines with the regular highlighting).
    """

    BLOCK_TAGS = ('div', 'p', 'pre')
    """The names of tags that are padded with vertical whitespace."""

    def __init__(self, *args, **kw):
        """
        Initialize an :class:`HTMLConverter` object.

        :param callback: Optional keyword argument to specify a function that
                         will be called to process text fragments before they
                         are emitted on the output stream. Note that link text
                         and preformatted text fragments are not processed by
                         this callback.
        :param output: Optional keyword argument to redirect the output to the
                       given file-like object. If this is not given a new
                       :class:`python3:~io.StringIO` object is created.
        """
        # Hide our optional keyword arguments from the superclass.
        self.callback = kw.pop("callback", None)
        self.output = kw.pop("output", None)
        # Initialize the superclass.
        HTMLParser.__init__(self, *args, **kw)

    def __call__(self, data):
        """
        Reset the parser, convert some HTML and get the text with ANSI escape sequences.

        :param data: The HTML to convert to text (a string).
        :returns: The converted text (only in case `output` is
                  a :class:`~python3:io.StringIO` object).
        """
        self.reset()
        self.feed(data)
        self.close()
        if isinstance(self.output, StringIO):
            return compact_empty_lines(self.output.getvalue())

    @property
    def current_style(self):
        """Get the current style from the top of the stack (a dictionary)."""
        return self.stack[-1] if self.stack else {}

    def close(self):
        """
        Close previously opened ANSI escape sequences.

        This method overrides the same method in the superclass to ensure that
        an :data:`.ANSI_RESET` code is emitted when parsing reaches the end of
        the input but a style is still active. This is intended to prevent
        malformed HTML from messing up terminal output.
        """
        if any(self.stack):
            self.output.write(ANSI_RESET)
            self.stack = []
        HTMLParser.close(self)

    def emit_style(self, style=None):
        """
        Emit an ANSI escape sequence for the given or current style to the output stream.

        :param style: A dictionary with arguments for :func:`ansi_style()` or
                      :data:`None`, in which case the style at the top of the
                      stack is emitted.
        """
        # Clear the current text styles.
        self.output.write(ANSI_RESET)
        # Apply a new text style?
        style = self.current_style if style is None else style
        if style:
            self.output.write(ansi_style(**style))

    def handle_charref(self, value):
        """
        Process a decimal or hexadecimal numeric character reference.

        :param value: The decimal or hexadecimal value (a string).
        """
        self.output.write(unichr(int(value[1:], 16) if value.startswith('x') else int(value)))

    def handle_data(self, data):
        """
        Process textual data.

        :param data: The decoded text (a string).
        """
        if self.link_url:
            # Link text is captured literally so that we can reliably check
            # whether the text and the URL of the link are the same string.
            self.link_text = data
        elif self.callback and self.preformatted_text_level == 0:
            # Text that is not part of a link and not preformatted text is
            # passed to the user defined callback to allow for arbitrary
            # pre-processing.
            data = self.callback(data)
        # All text is emitted unmodified on the output stream.
        self.output.write(data)

    def handle_endtag(self, tag):
        """
        Process the end of an HTML tag.

        :param tag: The name of the tag (a string).
        """
        if tag in ('a', 'b', 'code', 'del', 'em', 'i', 'ins', 'pre', 's', 'strong', 'span', 'u'):
            old_style = self.current_style
            # The following conditional isn't necessary for well formed
            # HTML but prevents raising exceptions on malformed HTML.
            if self.stack:
                self.stack.pop(-1)
            new_style = self.current_style
            if tag == 'a':
                if self.urls_match(self.link_text, self.link_url):
                    # Don't render the URL when it's part of the link text.
                    self.emit_style(new_style)
                else:
                    self.emit_style(new_style)
                    self.output.write(' (')
                    self.emit_style(old_style)
                    self.output.write(self.render_url(self.link_url))
                    self.emit_style(new_style)
                    self.output.write(')')
            else:
                self.emit_style(new_style)
            if tag in ('code', 'pre'):
                self.preformatted_text_level -= 1
        if tag in self.BLOCK_TAGS:
            # Emit an empty line after block level tags.
            self.output.write('\n\n')

    def handle_entityref(self, name):
        """
        Process a named character reference.

        :param name: The name of the character reference (a string).
        """
        self.output.write(unichr(name2codepoint[name]))

    def handle_starttag(self, tag, attrs):
        """
        Process the start of an HTML tag.

        :param tag: The name of the tag (a string).
        :param attrs: A list of tuples with two strings each.
        """
        if tag in self.BLOCK_TAGS:
            # Emit an empty line before block level tags.
            self.output.write('\n\n')
        if tag == 'a':
            self.push_styles(color='blue', bright=True, underline=True)
            # Store the URL that the link points to for later use, so that we
            # can render the link text before the URL (with the reasoning that
            # this is the most intuitive way to present a link in a plain text
            # interface).
            self.link_url = next((v for n, v in attrs if n == 'href'), '')
        elif tag == 'b' or tag == 'strong':
            self.push_styles(bold=True)
        elif tag == 'br':
            self.output.write('\n')
        elif tag == 'code' or tag == 'pre':
            self.push_styles(color='yellow')
            self.preformatted_text_level += 1
        elif tag == 'del' or tag == 's':
            self.push_styles(strike_through=True)
        elif tag == 'em' or tag == 'i':
            self.push_styles(italic=True)
        elif tag == 'ins' or tag == 'u':
            self.push_styles(underline=True)
        elif tag == 'span':
            styles = {}
            css = next((v for n, v in attrs if n == 'style'), "")
            for rule in css.split(';'):
                name, _, value = rule.partition(':')
                name = name.strip()
                value = value.strip()
                if name == 'background-color':
                    styles['background'] = self.parse_color(value)
                elif name == 'color':
                    styles['color'] = self.parse_color(value)
                elif name == 'font-style' and value == 'italic':
                    styles['italic'] = True
                elif name == 'font-weight' and value == 'bold':
                    styles['bold'] = True
                elif name == 'text-decoration' and value == 'line-through':
                    styles['strike_through'] = True
                elif name == 'text-decoration' and value == 'underline':
                    styles['underline'] = True
            self.push_styles(**styles)

    def normalize_url(self, url):
        """
        Normalize a URL to enable string equality comparison.

        :param url: The URL to normalize (a string).
        :returns: The normalized URL (a string).
        """
        return re.sub('^mailto:', '', url)

    def parse_color(self, value):
        """
        Convert a CSS color to something that :func:`ansi_style()` understands.

        :param value: A string like ``rgb(1,2,3)``, ``#AABBCC`` or ``yellow``.
        :returns: A color value supported by :func:`ansi_style()` or :data:`None`.
        """
        # Parse an 'rgb(N,N,N)' expression.
        if value.startswith('rgb'):
            tokens = re.findall(r'\d+', value)
            if len(tokens) == 3:
                return tuple(map(int, tokens))
        # Parse an '#XXXXXX' expression.
        elif value.startswith('#'):
            value = value[1:]
            length = len(value)
            if length == 6:
                # Six hex digits (proper notation).
                return (
                    int(value[:2], 16),
                    int(value[2:4], 16),
                    int(value[4:6], 16),
                )
            elif length == 3:
                # Three hex digits (shorthand).
                return (
                    int(value[0], 16),
                    int(value[1], 16),
                    int(value[2], 16),
                )
        # Try to recognize a named color.
        value = value.lower()
        if value in ANSI_COLOR_CODES:
            return value

    def push_styles(self, **changes):
        """
        Push new style information onto the stack.

        :param changes: Any keyword arguments are passed on to :func:`.ansi_style()`.

        This method is a helper for :func:`handle_starttag()`
        that does the following:

        1. Make a copy of the current styles (from the top of the stack),
        2. Apply the given `changes` to the copy of the current styles,
        3. Add the new styles to the stack,
        4. Emit the appropriate ANSI escape sequence to the output stream.
        """
        prototype = self.current_style
        if prototype:
            new_style = dict(prototype)
            new_style.update(changes)
        else:
            new_style = changes
        self.stack.append(new_style)
        self.emit_style(new_style)

    def render_url(self, url):
        """
        Prepare a URL for rendering on the terminal.

        :param url: The URL to simplify (a string).
        :returns: The simplified URL (a string).

        This method pre-processes a URL before rendering on the terminal. The
        following modifications are made:

        - The ``mailto:`` prefix is stripped.
        - Spaces are converted to ``%20``.
        - A trailing parenthesis is converted to ``%29``.
        """
        url = re.sub('^mailto:', '', url)
        url = re.sub(' ', '%20', url)
        url = re.sub(r'\)$', '%29', url)
        return url

    def reset(self):
        """
        Reset the state of the HTML parser and ANSI converter.

        When `output` is a :class:`~python3:io.StringIO` object a new
        instance will be created (and the old one garbage collected).
        """
        # Reset the state of the superclass.
        HTMLParser.reset(self)
        # Reset our instance variables.
        self.link_text = None
        self.link_url = None
        self.preformatted_text_level = 0
        if self.output is None or isinstance(self.output, StringIO):
            # If the caller specified something like output=sys.stdout then it
            # doesn't make much sense to negate that choice here in reset().
            self.output = StringIO()
        self.stack = []

    def urls_match(self, a, b):
        """
        Compare two URLs for equality using :func:`normalize_url()`.

        :param a: A string containing a URL.
        :param b: A string containing a URL.
        :returns: :data:`True` if the URLs are the same, :data:`False` otherwise.

        This method is used by :func:`handle_endtag()` to omit the URL of a
        hyperlink (``<a href="...">``) when the link text is that same URL.
        """
        return self.normalize_url(a) == self.normalize_url(b)

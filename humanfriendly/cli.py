# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: January 4, 2018
# URL: https://humanfriendly.readthedocs.io

"""
Usage: humanfriendly [OPTIONS]

Human friendly input/output (text formatting) on the command
line based on the Python package with the same name.

Supported options:

  -c, --run-command

    Execute an external command (given as the positional arguments) and render
    a spinner and timer while the command is running. The exit status of the
    command is propagated.

  --format-table

    Read tabular data from standard input (each line is a row and each
    whitespace separated field is a column), format the data as a table and
    print the resulting table to standard output. See also the --delimiter
    option.

  -d, --delimiter=VALUE

    Change the delimiter used by --format-table to VALUE (a string). By default
    all whitespace is treated as a delimiter.

  -l, --format-length=LENGTH

    Convert a length count (given as the integer or float LENGTH) into a human
    readable string and print that string to standard output.

  -n, --format-number=VALUE

    Format a number (given as the integer or floating point number VALUE) with
    thousands separators and two decimal places (if needed) and print the
    formatted number to standard output.

  -s, --format-size=BYTES

    Convert a byte count (given as the integer BYTES) into a human readable
    string and print that string to standard output.

  -b, --binary

    Change the output of -s, --format-size to use binary multiples of bytes
    (base-2) instead of the default decimal multiples of bytes (base-10).

  -t, --format-timespan=SECONDS

    Convert a number of seconds (given as the floating point number SECONDS)
    into a human readable timespan and print that string to standard output.

  --parse-length=VALUE

    Parse a human readable length (given as the string VALUE) and print the
    number of metres to standard output.

  --parse-size=VALUE

    Parse a human readable data size (given as the string VALUE) and print the
    number of bytes to standard output.

  --demo

    Demonstrate changing the style and color of the terminal font using ANSI
    escape sequences.

  -h, --help

    Show this message and exit.
"""

# Standard library modules.
import functools
import getopt
import pipes
import subprocess
import sys

# Modules included in our package.
from humanfriendly import (
    format_length,
    format_number,
    format_size,
    format_table,
    format_timespan,
    parse_length,
    parse_size,
    Spinner,
    Timer,
)
from humanfriendly.terminal import (
    ANSI_COLOR_CODES,
    ANSI_TEXT_STYLES,
    HIGHLIGHT_COLOR,
    ansi_wrap,
    output,
    usage,
    warning
)


def main():
    """Command line interface for the ``humanfriendly`` program."""
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'cd:l:n:s:bt:h', [
            'run-command', 'format-table', 'delimiter=', 'format-length=',
            'format-number=', 'format-size=', 'binary', 'format-timespan=',
            'parse-length=', 'parse-size=', 'demo', 'help',
        ])
    except Exception as e:
        warning("Error: %s", e)
        sys.exit(1)
    actions = []
    delimiter = None
    should_format_table = False
    binary = any(o in ('-b', '--binary') for o, v in options)
    for option, value in options:
        if option in ('-d', '--delimiter'):
            delimiter = value
        elif option == '--parse-size':
            actions.append(functools.partial(print_parsed_size, value))
        elif option == '--parse-length':
            actions.append(functools.partial(print_parsed_length, value))
        elif option in ('-c', '--run-command'):
            actions.append(functools.partial(run_command, arguments))
        elif option in ('-l', '--format-length'):
            actions.append(functools.partial(print_formatted_length, value))
        elif option in ('-n', '--format-number'):
            actions.append(functools.partial(print_formatted_number, value))
        elif option in ('-s', '--format-size'):
            actions.append(functools.partial(print_formatted_size, value, binary))
        elif option == '--format-table':
            should_format_table = True
        elif option in ('-t', '--format-timespan'):
            actions.append(functools.partial(print_formatted_timespan, value))
        elif option == '--demo':
            actions.append(demonstrate_ansi_formatting)
        elif option in ('-h', '--help'):
            usage(__doc__)
            return
    if should_format_table:
        actions.append(functools.partial(print_formatted_table, delimiter))
    if not actions:
        usage(__doc__)
        return
    for partial in actions:
        partial()


def run_command(command_line):
    """Run an external command and show a spinner while the command is running."""
    timer = Timer()
    spinner_label = "Waiting for command: %s" % " ".join(map(pipes.quote, command_line))
    with Spinner(label=spinner_label, timer=timer) as spinner:
        process = subprocess.Popen(command_line)
        while True:
            spinner.step()
            spinner.sleep()
            if process.poll() is not None:
                break
    sys.exit(process.returncode)


def print_formatted_length(value):
    """Print a human readable length."""
    if '.' in value:
        output(format_length(float(value)))
    else:
        output(format_length(int(value)))


def print_formatted_number(value):
    """Print large numbers in a human readable format."""
    output(format_number(float(value)))


def print_formatted_size(value, binary):
    """Print a human readable size."""
    output(format_size(int(value), binary=binary))


def print_formatted_table(delimiter):
    """Read tabular data from standard input and print a table."""
    data = []
    for line in sys.stdin:
        line = line.rstrip()
        data.append(line.split(delimiter))
    output(format_table(data))


def print_formatted_timespan(value):
    """Print a human readable timespan."""
    output(format_timespan(float(value)))


def print_parsed_length(value):
    """Parse a human readable length and print the number of metres."""
    output(parse_length(value))


def print_parsed_size(value):
    """Parse a human readable data size and print the number of bytes."""
    output(parse_size(value))


def demonstrate_ansi_formatting():
    """Demonstrate the use of ANSI escape sequences."""
    # First we demonstrate the supported text styles.
    output("%s", ansi_wrap("Text styles:", bold=True))
    styles = ['normal', 'bright']
    styles.extend(ANSI_TEXT_STYLES.keys())
    for style_name in sorted(styles):
        options = dict(color=HIGHLIGHT_COLOR)
        if style_name != 'normal':
            options[style_name] = True
        style_label = style_name.replace('_', ' ').capitalize()
        output(" - %s", ansi_wrap(style_label, **options))
    # Now we demonstrate the supported colors.
    intensities = [
        ('faint', dict(faint=True)),
        ('normal', dict()),
        ('bright', dict(bright=True)),
    ]
    output("\n%s" % ansi_wrap("Color intensities:", bold=True))
    output(format_table([
        [color_name] + [
            ansi_wrap("XXXXXX", color=color_name, **kw)
            for label, kw in intensities
        ]
        for color_name in sorted(ANSI_COLOR_CODES.keys())
    ], column_names=["Color", "Faint", "Normal", "Bright"]))

# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: May 25, 2015
# URL: https://humanfriendly.readthedocs.org

"""
Usage: humanfriendly [OPTIONS]

Human friendly input/output (text formatting) on the command
line based on the Python package with the same name.

Supported options:

  -c, --run-command

    Execute an external command (given as the positional arguments) and render
    a spinner and timer while the command is running. The exit status of the
    command is propagated.

  -n, --format-number=VALUE

    Format a number (given as the integer or floating point number VALUE) with
    thousands separators and two decimal places (if needed) and print the
    formatted number to standard output.

  -s, --format-size=BYTES

    Convert a byte count (given as the integer BYTES) into a human readable
    string and print that string to standard output.

  -t, --format-timespan=SECONDS

    Convert a number of seconds (given as the floating point number SECONDS)
    into a human readable timespan and print that string to standard output.

  --parse-size=VALUE

    Parse a human readable data size (given as the string VALUE) and print the
    number of bytes to standard output.

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
from humanfriendly import format_number, format_size, format_timespan, parse_size, Spinner, Timer


def main():
    """Command line interface for the ``humanfriendly`` program."""
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'chn:s:t:', [
            'format-number=', 'format-size=', 'format-timespan=', 'help',
            'parse-size=', 'run-command',
        ])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: %s\n" % e)
        sys.exit(1)
    actions = []
    for option, value in options:
        if option == '--parse-size':
            actions.append(functools.partial(print_parsed_size, value))
        elif option in ('-c', '--run-command'):
            actions.append(functools.partial(run_command, arguments))
        elif option in ('-n', '--format-number'):
            actions.append(functools.partial(print_formatted_number, value))
        elif option in ('-s', '--format-size'):
            actions.append(functools.partial(print_formatted_size, value))
        elif option in ('-t', '--format-timespan'):
            actions.append(functools.partial(print_formatted_timespan, value))
        elif option in ('-h', '--help'):
            usage()
            return
    if not actions:
        usage()
        return
    for partial in actions:
        partial()


def usage():
    """Print a friendly usage message to the terminal."""
    print(__doc__.strip())


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


def print_formatted_number(value):
    """Print large numbers in a human readable format."""
    print(format_number(float(value)))


def print_formatted_size(value):
    """Print a human readable size."""
    print(format_size(int(value)))


def print_formatted_timespan(value):
    """Print a human readable timespan."""
    print(format_timespan(float(value)))


def print_parsed_size(value):
    """Parse a human readable data size and print the number of bytes."""
    print(parse_size(value))

#!/usr/bin/env python

# Tests for the 'humanfriendly' module.
#
# Author: Peter Odding <peter.odding@paylogic.eu>
# Last Change: March 29, 2015
# URL: https://humanfriendly.readthedocs.org

# Standard library modules.
import math
import os
import time
import unittest

try:
    # Python 2.x.
    from StringIO import StringIO
except ImportError:
    # Python 3.x.
    from io import StringIO

# The module we are testing.
import humanfriendly

class HumanFriendlyTestCase(unittest.TestCase):

    def test_pluralization(self):
        self.assertEqual('1 word', humanfriendly.pluralize(1, 'word'))
        self.assertEqual('2 words', humanfriendly.pluralize(2, 'word'))
        self.assertEqual('1 box', humanfriendly.pluralize(1, 'box', 'boxes'))
        self.assertEqual('2 boxes', humanfriendly.pluralize(2, 'box', 'boxes'))

    def test_boolean_coercion(self):
        for value in [True, 'TRUE', 'True', 'true', 'on', 'yes', '1']:
            self.assertEqual(True, humanfriendly.coerce_boolean(value))
        for value in [False, 'FALSE', 'False', 'false', 'off', 'no', '0']:
            self.assertEqual(False, humanfriendly.coerce_boolean(value))
        self.assertRaises(ValueError, humanfriendly.coerce_boolean, 'not a boolean')

    def test_format_timespan(self):
        minute = 60
        hour = minute * 60
        day = hour * 24
        week = day * 7
        year = week * 52
        self.assertEqual('0 seconds', humanfriendly.format_timespan(0))
        self.assertEqual('0.54 seconds', humanfriendly.format_timespan(0.54321))
        self.assertEqual('1 second', humanfriendly.format_timespan(1))
        self.assertEqual('3.14 seconds', humanfriendly.format_timespan(math.pi))
        self.assertEqual('1 minute', humanfriendly.format_timespan(minute))
        self.assertEqual('1 minute and 20 seconds', humanfriendly.format_timespan(80))
        self.assertEqual('2 minutes', humanfriendly.format_timespan(minute * 2))
        self.assertEqual('1 hour', humanfriendly.format_timespan(hour))
        self.assertEqual('2 hours', humanfriendly.format_timespan(hour * 2))
        self.assertEqual('1 day', humanfriendly.format_timespan(day))
        self.assertEqual('2 days', humanfriendly.format_timespan(day * 2))
        self.assertEqual('1 week', humanfriendly.format_timespan(week))
        self.assertEqual('2 weeks', humanfriendly.format_timespan(week * 2))
        self.assertEqual('1 year', humanfriendly.format_timespan(year))
        self.assertEqual('2 years', humanfriendly.format_timespan(year * 2))
        self.assertEqual('1 year, 2 weeks and 3 days', humanfriendly.format_timespan(year + week * 2 + day * 3 + hour * 12))

    def test_parse_date(self):
        self.assertEqual((2013, 6, 17, 0, 0, 0), humanfriendly.parse_date('2013-06-17'))
        self.assertEqual((2013, 6, 17, 2, 47, 42), humanfriendly.parse_date('2013-06-17 02:47:42'))
        self.assertRaises(humanfriendly.InvalidDate, humanfriendly.parse_date, '2013-06-XY')

    def test_format_size(self):
        self.assertEqual('0 bytes', humanfriendly.format_size(0))
        self.assertEqual('1 byte', humanfriendly.format_size(1))
        self.assertEqual('42 bytes', humanfriendly.format_size(42))
        self.assertEqual('1 KB', humanfriendly.format_size(1024 ** 1))
        self.assertEqual('1 MB', humanfriendly.format_size(1024 ** 2))
        self.assertEqual('1 GB', humanfriendly.format_size(1024 ** 3))
        self.assertEqual('1 TB', humanfriendly.format_size(1024 ** 4))
        self.assertEqual('1 PB', humanfriendly.format_size(1024 ** 5))

    def test_parse_size(self):
        self.assertEqual(0, humanfriendly.parse_size('0B'))
        self.assertEqual(42, humanfriendly.parse_size('42'))
        self.assertEqual(42, humanfriendly.parse_size('42B'))
        self.assertEqual(1024, humanfriendly.parse_size('1k'))
        self.assertEqual(1024, humanfriendly.parse_size('1 KB'))
        self.assertEqual(1024, humanfriendly.parse_size('1 kilobyte'))
        self.assertEqual(1024 ** 3, humanfriendly.parse_size('1 GB'))
        self.assertRaises(humanfriendly.InvalidSize, humanfriendly.parse_size, '1z')
        self.assertRaises(humanfriendly.InvalidSize, humanfriendly.parse_size, 'a')

    def test_round_number(self):
        self.assertEqual('1', humanfriendly.round_number(1))
        self.assertEqual('1', humanfriendly.round_number(1.0))
        self.assertEqual('1.00', humanfriendly.round_number(1, keep_width=True))
        self.assertEqual('3.14', humanfriendly.round_number(3.141592653589793))

    def test_format_path(self):
        friendly_path = os.path.join('~', '.vimrc')
        absolute_path = os.path.join(os.environ['HOME'], '.vimrc')
        self.assertEqual(friendly_path, humanfriendly.format_path(absolute_path))

    def test_parse_path(self):
        friendly_path = os.path.join('~', '.vimrc')
        absolute_path = os.path.join(os.environ['HOME'], '.vimrc')
        self.assertEqual(absolute_path, humanfriendly.parse_path(friendly_path))

    def test_concatenate(self):
        self.assertEqual(humanfriendly.concatenate([]), '')
        self.assertEqual(humanfriendly.concatenate(['one']), 'one')
        self.assertEqual(humanfriendly.concatenate(['one', 'two']), 'one and two')
        self.assertEqual(humanfriendly.concatenate(['one', 'two', 'three']), 'one, two and three')

    def test_timer(self):
        for seconds, text in ((1, '1 second'),
                              (2, '2 seconds'),
                              (60, '1 minute'),
                              (60*2, '2 minutes'),
                              (60*60, '1 hour'),
                              (60*60*2, '2 hours'),
                              (60*60*24, '1 day'),
                              (60*60*24*2, '2 days'),
                              (60*60*24*7, '1 week'),
                              (60*60*24*7*2, '2 weeks')):
            t = humanfriendly.Timer(time.time() - seconds)
            self.assertEqual(humanfriendly.round_number(t.elapsed_time, keep_width=True), '%i.00' % seconds)
            self.assertEqual(str(t), text)
        # Test rounding to seconds.
        t = humanfriendly.Timer(time.time() - 2.2)
        self.assertEqual(t.rounded, '2 seconds')
        # Test automatic timer.
        automatic_timer = humanfriendly.Timer()
        time.sleep(1)
        self.assertEqual(normalize_timestamp(humanfriendly.round_number(automatic_timer.elapsed_time, keep_width=True)), '1.00')
        # Test resumable timer.
        resumable_timer = humanfriendly.Timer(resumable=True)
        for i in range(2):
            with resumable_timer:
                time.sleep(1)
        self.assertEqual(normalize_timestamp(humanfriendly.round_number(resumable_timer.elapsed_time, keep_width=True)), '2.00')

    def test_spinner(self):
        stream = StringIO()
        spinner = humanfriendly.Spinner('test spinner', total=4, stream=stream, interactive=True)
        for progress in [1, 2, 3, 4]:
            spinner.step(progress=progress)
            time.sleep(0.2)
        spinner.clear()
        lines = [line for line in stream.getvalue().split(humanfriendly.erase_line_code) if line]
        self.assertTrue(len(lines) > 0)
        self.assertTrue(all('test spinner' in l for l in lines))
        self.assertTrue(all('%' in l for l in lines))
        self.assertEqual(sorted(set(lines)), sorted(lines))

    def test_automatic_spinner(self):
        # There's not a lot to test about the AutomaticSpinner class, but by at
        # least running it here we are assured that the code functions on all
        # supported Python versions. AutomaticSpinner is built on top of the
        # Spinner class so at least we also have the tests for the Spinner
        # class to back us up.
        with humanfriendly.AutomaticSpinner('test spinner'):
            time.sleep(1)

    def test_prompt_for_choice(self):
        interactive_prompt = humanfriendly.interactive_prompt
        try:
            # Choice selection by full string match.
            humanfriendly.interactive_prompt = lambda prompt: 'foo'
            self.assertEqual(humanfriendly.prompt_for_choice(['foo', 'bar']), 'foo')
            # Choice selection by substring input.
            humanfriendly.interactive_prompt = lambda prompt: 'f'
            self.assertEqual(humanfriendly.prompt_for_choice(['foo', 'bar']), 'foo')
            # Choice selection by number.
            humanfriendly.interactive_prompt = lambda prompt: '2'
            self.assertEqual(humanfriendly.prompt_for_choice(['foo', 'bar']), 'bar')
            # Choice selection by going with the default.
            humanfriendly.interactive_prompt = lambda prompt: ''
            self.assertEqual(humanfriendly.prompt_for_choice(['foo', 'bar'], default='bar'), 'bar')
            # Invalid substrings are refused.
            responses = ['', 'q', 'z']
            humanfriendly.interactive_prompt = lambda prompt: responses.pop(0)
            self.assertEqual(humanfriendly.prompt_for_choice(['foo', 'bar', 'baz']), 'baz')
            # Choice selection by substring input requires an unambiguous substring match.
            responses = ['a', 'q']
            humanfriendly.interactive_prompt = lambda prompt: responses.pop(0)
            self.assertEqual(humanfriendly.prompt_for_choice(['foo', 'bar', 'baz', 'qux']), 'qux')
            # Invalid numbers are refused.
            responses = ['42', '2']
            humanfriendly.interactive_prompt = lambda prompt: responses.pop(0)
            self.assertEqual(humanfriendly.prompt_for_choice(['foo', 'bar', 'baz']), 'bar')
        finally:
            humanfriendly.interactive_prompt = interactive_prompt

def normalize_timestamp(value, ndigits=1):
    return '%.2f' % round(float(value), ndigits=ndigits)

if __name__ == '__main__':
    unittest.main()

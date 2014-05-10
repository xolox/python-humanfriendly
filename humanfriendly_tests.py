#!/usr/bin/env python

# Tests for the 'humanfriendly' module.
#
# Author: Peter Odding <peter.odding@paylogic.eu>
# Last Change: May 11, 2014
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
        self.assertEqual(42, humanfriendly.parse_size('42'))
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
        abspath = os.path.join(os.environ['HOME'], '.vimrc')
        self.assertEqual(os.path.join('~', '.vimrc'), humanfriendly.format_path(abspath))

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
        t = humanfriendly.Timer()
        time.sleep(1)
        self.assertEqual(humanfriendly.round_number(t.elapsed_time, keep_width=True), '1.00')
        self.assertEqual(str(t), '1 second')

    def test_spinner(self):
        stream = StringIO()
        spinner = humanfriendly.Spinner('test spinner', stream=stream)
        for i in range(4):
            spinner.step()
        lines = stream.getvalue().splitlines()
        self.assertTrue(all('test spinner' in l for l in lines))
        self.assertEqual(sorted(set(lines)), sorted(lines))

if __name__ == '__main__':
    unittest.main()

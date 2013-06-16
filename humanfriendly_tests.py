#!/usr/bin/env python

# Tests for the 'humanfriendly' module.
#
# Author: Peter Odding <peter.odding@paylogic.eu>
# Last Change: June 17, 2013
# URL: https://github.com/xolox/python-human-friendly

# Standard library modules.
import os
import unittest

# The module we are testing.
import humanfriendly

class HumanFriendlyTestCase(unittest.TestCase):

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
      try:
        humanfriendly.parse_size('1z')
        self.assertTrue(False)
      except Exception, e:
        self.assertTrue(isinstance(e, humanfriendly.InvalidSize))

    def test_round_size(self):
      self.assertEqual('1', humanfriendly.round_size(1))
      self.assertEqual('1', humanfriendly.round_size(1.0))
      self.assertEqual('1.00', humanfriendly.round_size(1, keep_width=True))
      self.assertEqual('3.14', humanfriendly.round_size(3.141592653589793))

    def test_format_path(self):
      abspath = os.path.join(os.environ['HOME'], '.vimrc')
      self.assertEqual(os.path.join('~', '.vimrc'), humanfriendly.format_path(abspath))

if __name__ == '__main__':
    unittest.main()

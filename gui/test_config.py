#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

from config import Config
import unittest

class TestConfig(unittest.TestCase):
    """Testing the Config module"""

    def test_getset(self):
        conf = Config.Instance()
        self.assertIsNone(conf.get('foo.bar'))
        conf.set('foo.bar', 'value')
        self.assertEqual(conf.get('foo.bar'), 'value')

        conf2 = Config.Instance()
        self.assertEqual(conf2.get('foo.bar'), 'value')

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python

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

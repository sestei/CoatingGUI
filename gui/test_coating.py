#!/usr/bin/python

import coating
import unittest

class TestCoating(unittest.TestCase):
    """Testing the Coating module"""

    def test_layer(self):
        l = coating.Layer("1.0", 100)
        self.assertAlmostEqual(l.material.n(1), 1.0)
        self.assertEqual(l.thickness, 100)

    def test_coating(self):
        c = coating.Coating("1.0", "1.45", [(1.45,200),(2.1,100)])
        self.assertEqual(len(c.layers), 2)
        self.assertAlmostEqual(c.superstrate.n(1), 1.0)
        self.assertAlmostEqual(c.substrate.n(1), 1.45)
        self.assertAlmostEqual(c.layers[0].material.n(1), 1.45)
        self.assertAlmostEqual(c.layers[1].material.n(1), 2.1)
        self.assertAlmostEqual(c.layers[1].thickness, 100)
        self.assertAlmostEqual(c.thickness, 300)

if __name__ == '__main__':
    unittest.main()

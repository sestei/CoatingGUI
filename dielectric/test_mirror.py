#!/usr/bin/python

import mirror
import unittest

class TestMirror(unittest.TestCase):
    def test_init(self):
        m = mirror.Mirror(wavelength = 2.0)
        self.assertEqual(m.wavelength, 2.0)
        rs, rp = m.get_reflectivity()
        self.assertAlmostEqual(rp*100, 3.5, 1)
        self.assertAlmostEqual(rs*100, 3.5, 1)

    def test_dichroic_808_1064(self):
        m = mirror.Mirror(wavelength=1064, n_subs=1.52)
        d = [364,114,181,113,181,113,178,112,178,115,178,111,173,108,196,129]
        n = [1.45,2.35] * 8
        m.add_layers_direct(n, d)
        rs,_ = m.get_reflectivity(1064)
        self.assertAlmostEqual(rs, 0.99863, 5)
        rs,_ = m.get_reflectivity(808)
        self.assertAlmostEqual(rs, 0.000242, 6)

    def test_aoi_1550(self):
        m = mirror.Mirror(wavelength=1550, n_subs=1.45)
        d = [112, 267, 112, 267, 112, 534]
        n = [3.48,1.45] * 3
        m.add_layers_direct(n, d)
        rs,rp = m.get_reflectivity(AOI=30)
        print m.stack.alpha_0
        print rs,rp

if __name__ == '__main__':
    unittest.main()
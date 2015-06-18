#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import unittest
import fresnel
import numpy as np

class TestFresnel(unittest.TestCase):
    """Testing the fresnel module"""

    def test_angle(self):
        a = fresnel.angle(np.pi/4, 1.0, 1.0)
        self.assertAlmostEqual(a, np.pi/4, 7)

        n = np.arange(1, 1.5, 10)
        a = fresnel.angle(np.pi/4, 1.0, n)
        self.assertEqual(len(n), len(a))
        self.assertAlmostEqual(a[0], np.pi/4, 7)

    def test_rho(self):
        rs, rp = fresnel.rho(0, 1, 0, 1)
        self.assertAlmostEqual(rs, 0, 7)
        self.assertAlmostEqual(rp, 0, 7)

        # testing brewster's angle
        n1 = 1.0
        n2 = 1.46
        alpha_0 = np.arctan(n2/n1)
        alpha_1 = fresnel.angle(alpha_0, n1, n2)
        rs, rp = fresnel.rho(alpha_0, n1, alpha_1, n2)
        self.assertAlmostEqual(rp, 0, 7)

if __name__ == '__main__':
    unittest.main()

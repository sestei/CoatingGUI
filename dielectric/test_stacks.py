import unittest
import stacks
import numpy as np

class TestStack(unittest.TestCase):
    """Testing the stack module"""

    def setUp(self):
        self.stack = stacks.Stack(
            [1.0, 1.0, 1.0, 1.0],
            [0.25, 0.25],
            45.0
            )

    def test_properties(self):
        self.stack.alpha_0 = 30
        self.assertAlmostEqual(self.stack.alpha_0, 30, 7)

        self.stack.stacks_d[0] = 0.5
        self.assertAlmostEqual(self.stack.stacks_d[0], 0.5, 7)

        self.stack.stacks_n[0] = 1.5
        self.assertAlmostEqual(self.stack.stacks_n[0], 1.5, 7)

    def test_valid(self):
        self.stack.update()
        self.assertTrue(self.stack.is_valid())
        self.stack.alpha_0 = 10.0
        self.assertFalse(self.stack.is_valid())
        self.stack.update()
        self.assertTrue(self.stack.is_valid())
        self.stack.stacks_d = [0.5, 0.5]
        self.assertTrue(self.stack.is_valid())
        self.stack.stacks_n = [1.3, 1.0]
        self.assertFalse(self.stack.is_valid())

    def test_update_angles(self):
        self.stack.alpha_0 = 45.0
        self.stack._update_angles()
        self.assertTrue(self.stack._angles_valid)
        self.assertAlmostEqual(self.stack._stacks_a[1], np.deg2rad(45), 7)

    def test_update_rhos(self):
        self.stack.stacks_n[1] = 1.5
        self.stack._update_rhos()
        self.assertTrue(self.stack._valid)
        rs, rp = self.stack.stacks_rho[1]
        self.assertGreater(rs**2, 0)
        self.assertGreater(rp**2, 0)

    def test_reflectivity(self):
        """
        Simulate HR@1064nm, HT@808nm stack, check reflectivity at 1064nm
        """
        n_sio = 1.45
        n_ta = 2.35

        stacks_n = np.array([1.0,n_sio] + [n_ta, n_sio]*8)
        stacks_n[-1] = 1.52
        stacks_d = np.array([364,114,181,113,181,113,178,112,178,115,178,111,173,108,196,129])
        stack = stacks.Stack(stacks_n, stacks_d)

        rs, rp = stack.reflectivity(1064)

        self.assertAlmostEqual(rs, 0.999315645, 8)
        self.assertAlmostEqual(rp, 0.999315645, 8)

if __name__ == '__main__':
    unittest.main()

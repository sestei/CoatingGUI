#!/usr/bin/python
import unittest
from stackbuilder import *

class TestStackBuilder(unittest.TestCase):
    def test_quarter_wave_stack(self):
        n_stacks = [1.0, 1.0]
        n_air_subs = [1.0, 2.0]
        wavelength = 1.0
        stack = quarter_wave_stack(1, n_stacks, n_air_subs, wavelength)
        self.assertTrue(np.all(
            stack.stacks_n == np.array([1.0, 1.0, 1.0, 2.0])))
        self.assertTrue(np.all(
            stack.stacks_d == np.array([0.25, 0.25])))

    def test_capped_quarter_wave_stack(self):
        n_stacks = [1.0, 1.0]
        n_air_subs = [1.0, 2.0]
        wavelength = 1.0
        stack = capped_quarter_wave_stack(1, n_stacks, n_air_subs, 2.0, wavelength)
        self.assertTrue(np.all(
            stack.stacks_n == np.array([1.0, 2.0, 1.0, 1.0, 2.0])))
        self.assertTrue(np.all(
            stack.stacks_d == np.array([.25, 0.25, 0.25])))

    def test_quarter_wave_stack_angle(self):
        stack = StackBuilder.half_wave_stack(1, [1.0, 1.0], [1.0, 2.0], 1.0, 45.0)

if __name__ == '__main__':
    unittest.main()
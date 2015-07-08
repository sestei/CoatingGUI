#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import unittest
import os
from utils import *

def open_file(filename):
    return DataFileWrapper(filename)

class TestDataFileWrapper(unittest.TestCase):
    """Test the DataFileWrapper class"""

    def setUp(self):
        fn = open('tmp_data_file.dat', 'w')
        fn.write('100\t10\n200\t20\n250\t25\n')
        fn.close()

    def tearDown(self):
        os.remove('tmp_data_file.dat')

    def test_nonexisting_file(self):
        self.assertRaises(UnreadableFile, open_file, 'does_not_exist.dat')
        
    def test_unreadable_file(self):
        fn = open('tmp_unreadable_file.dat', 'w')
        fn.write('???')
        fn.close()
        self.assertRaises(UnexpectedFileLayout, open_file, 'tmp_unreadable_file.dat')
        os.remove('tmp_unreadable_file.dat')

    def test_wrong_shape(self):
        fn = open('tmp_wrong_shape_file.dat', 'w')
        fn.write('100\t10\t20\n')
        fn.close()
        self.assertRaises(UnexpectedFileLayout, open_file, 'tmp_wrong_shape_file.dat')
        os.remove('tmp_wrong_shape_file.dat')


    def test_data_file(self):
        dfw = DataFileWrapper('tmp_data_file.dat')

    def test_data_interpolation(self):
        dfw = DataFileWrapper('tmp_data_file.dat')
        self.assertAlmostEqual(dfw.value(100), 10)
        self.assertAlmostEqual(dfw.value(150), 15)
        self.assertAlmostEqual(dfw.value(300), 25)
        self.assertAlmostEqual(dfw.value(0), 10)
        self.assertAlmostEqual(dfw.value(-100), 10)

if __name__ == '__main__':
    unittest.main()

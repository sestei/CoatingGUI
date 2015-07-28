#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import numpy as np

class UnexpectedFileLayout(Exception):
    pass

class UnreadableFile(Exception):
    pass

class DataFileWrapper(object):
    def __init__(self, filename):
        self.filename = filename
        self.read_file()

    def value(self, x):
        return np.interp(x, self._x, self._y)

    def read_file(self):
        try:
            x, y = np.loadtxt(self.filename, ndmin=2, unpack=True)
        except IOError as e:
            raise UnreadableFile(str(e))
        except ValueError as e:
            raise UnexpectedFileLayout(
                'Unexpected format of data file.')

        self._x = x
        self._y = y
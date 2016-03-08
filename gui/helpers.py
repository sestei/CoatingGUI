#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import numpy as np
from contextlib import contextmanager
from PyQt4.QtGui import QMessageBox
from version import version_string


def export_data(filename, xdata, ydata, labels):
    """
    Exports data from xdata, ydata as ASCII file (tab-separated).

    xdata and ydata should be arrays with (possibly) multiple data sets.
    """
    X = xdata[0]
    unionised = False

    # combine multiple x datasets into one, interpolating y data
    if len(xdata) > 1:
        unionised = True
        for ii in range(1, len(xdata)):
            X = np.union1d(X, xdata[ii])
    Y = []
    for ii in range(len(ydata)):
        if unionised:
            Y.append(np.interp(X, xdata[ii], ydata[ii]))
        else:
            Y.append(ydata[ii])

    data = np.vstack((X, Y))

    header = version_string + "\n\n" + "\t".join(labels)
    np.savetxt(filename, data.T, delimiter="\t", fmt='%.5g', header=header)


@contextmanager
def block_signals(obj):
    """
    Context Manager for use in with statements, temporarily
    disables signals from a QObject
    """
    state = obj.blockSignals(True)
    try:
        yield obj
    finally:
        obj.blockSignals(state)


def to_float(number):
    """Converts a floating point number to a sensible string representation"""
    return '{0:g}'.format(number)
    
def int_conversion_error(text, parent=None):
    QMessageBox.critical(parent, 'Conversion Error',
       'The input "{0}" could not be converted to an integer number.'.format(text))

def float_conversion_error(text, parent=None):
    QMessageBox.critical(parent, 'Conversion Error',
        'The input "{0}" could not be converted to an integer number.'.format(text))

def float_set_from_lineedit(widget, config, key, parent=None):
    if widget.isModified():
        text = widget.text()
        try:
            config.set(key, float(text))
        except ValueError:
            float_conversion_error(text, parent)

def int_set_from_lineedit(widget, config, key, parent=None):
    if widget.isModified():
        text = widget.text()
        try:
            config.set(key, int(text))
        except ValueError:
            int_conversion_error(text, parent)

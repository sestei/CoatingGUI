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

def get_L_H_designation(material_names, coating, lambda0):
    materials = [l.material for l in coating.layers]

def get_designations(coating, lambda0):
    materials = [l.material for l in coating.layers]
    material_names = list(set([m.name for m in materials]))
    if len(material_names) == 2:
        order = ['L', 'H']
        m0 = next(m for m in materials if m.name == material_names[0])
        m1 = next(m for m in materials if m.name == material_names[1])
        if m0.n(lambda0) > m1.n(lambda0):
            order.reverse()
    else:
        order = ['M{0}'.format(ii+1) for ii in range(len(material_names))]

    designations = {}
    for ii, mm in enumerate(material_names):
        designations[mm] = order[ii]
    return designations

def export_stack_formula(coating, lambda0, filename):
    # use frozenset to create unique set of materials?
    # can then build dictionary which assigns either H and L to those
    # materials, or something as simple as A, B, C, D, ... if many materials
    with open(filename, 'w') as fp:
        fp.write('Superstrate: {0}\n'.format(coating.superstrate.name))
        fp.write('Substrate: {0}\n'.format(coating.substrate.name))

        designations = get_designations(coating, lambda0)
        for m, d in designations.iteritems():
            fp.write('{0}: {1}\n'.format(d, m))

        formula = []
        for l in coating.layers:
            m = l.material
            qwl = lambda0/(4*m.n(lambda0))
            formula.append('{0:.3f}{1}'.format(l.thickness/qwl, designations[m.name]))

        formula.reverse()
        fp.write(' '.join(formula))
        fp.write('\n')


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

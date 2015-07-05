#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import baseplot
import numpy as np
import matplotlib
from PyQt4.QtCore import pyqtSlot
from mixins import YAxisLimits, XAxisLimits, XAxisSteps

class PhasePlot(baseplot.BasePlot):
    def __init__(self, handle):
        super(PhasePlot, self).__init__('phase', handle)

    def plot(self, coating):
        #TODO: refactor this into another function, which can be used to plot transmission as well
        
        if self.config.get('xaxis.limits') == 'auto':
            lambda0 = self.config.parent.get('coating.lambda0')
            xlim = [0.7 * lambda0, 1.3 * lambda0]
        else:
            xlim = [self.config.get('xaxis.min'),
                    self.config.get('xaxis.max')]
        
        X = np.linspace(*xlim, num=self.config.get('xaxis.steps'))
        Y = np.zeros((len(X), 3))

        AOI = self.config.parent.get('coating.AOI')
        for step in range(len(X)):
            stack = coating.create_stack(X[step], AOI=AOI)
            Y[step,:] = stack.phase(X[step])

        handles = self.handle.plot(X,(np.unwrap(Y, axis=0)%(2*np.pi))*180/np.pi)

        self.add_grid()
        self.handle.set_xlim(xlim)
        if self.config.get('yaxis.limits') == 'user':
            self.handle.set_ylim(
                self.config.get('yaxis.min'),
                self.config.get('yaxis.max'))

        self.handle.set_xlabel('Wavelength (nm)')
        self.handle.set_ylabel('Phase (deg)')
        self.add_legend(handles, ['s pol', 'p pol', 'delta'])
        self.add_copyright()


class PhaseOptions(XAxisLimits, YAxisLimits, XAxisSteps,
                   baseplot.BasePlotOptionWidget):
    def __init__(self, parent):
        super(PhaseOptions, self).__init__('phase', parent)

    def initialise_options(self):
        super(PhaseOptions, self).initialise_options()


info = {
    'phase': {
        'description': 'Phase over Wavelength',
        'plotter': PhasePlot,
        'options': PhaseOptions,
    }
}
#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import baseplot
import numpy as np
import matplotlib
from PyQt4.QtCore import pyqtSlot
from gui.utils import to_float

class PhasePlot(baseplot.BasePlot):
    def plot(self, coating):
        #TODO: refactor this into another function, which can be used to plot transmission as well
        
        if self.config.get('plot.phase.xaxis.limits') == 'auto':
            lambda0 = self.config.get('coating.lambda0')
            xlim = [0.7 * lambda0, 1.3 * lambda0]
        else:
            xlim = [self.config.get('plot.phase.xaxis.min'),
                    self.config.get('plot.phase.xaxis.max')]
        
        X = np.linspace(*xlim, num=self.config.get('plot.phase.xaxis.steps'))
        Y = np.zeros((len(X), 3))

        AOI = self.config.get('coating.AOI')
        for step in range(len(X)):
            stack = coating.create_stack(X[step], AOI=AOI)
            Y[step,:] = stack.phase(X[step])

        handles = self.handle.plot(X,(np.unwrap(Y, axis=0)%(2*np.pi))*180/np.pi)

        self.add_grid()
        self.handle.set_xlim(xlim)
        if self.config.get('plot.phase.yaxis.limits') == 'user':
            self.handle.set_ylim(
                self.config.get('plot.phase.yaxis.min'),
                self.config.get('plot.phase.yaxis.max'))

        self.handle.set_xlabel('Wavelength (nm)')
        self.handle.set_ylabel('Phase (deg)')
        self.add_legend(handles, ['s pol', 'p pol', 'delta'])
        self.add_copyright()


class PhaseOptions(baseplot.BasePlotOptionWidget):
    def __init__(self, parent):
        super(PhaseOptions, self).__init__('Phase', parent)

    def initialise_options(self):
        if self.config.get('plot.phase.xaxis.limits') == 'auto':
            self.rbXLimAuto.setChecked(True)
        else:
            self.rbXLimUser.setChecked(True)
        
        if self.config.get('plot.phase.yaxis.limits') == 'auto':
            self.rbYLimAuto.setChecked(True)
        else:
            self.rbYLimUser.setChecked(True)

        self.txtXSteps.setText(to_float(self.config.get('plot.phase.xaxis.steps')))
        self.txtXLimMin.setText(to_float(self.config.get('plot.phase.xaxis.min')))
        self.txtXLimMax.setText(to_float(self.config.get('plot.phase.xaxis.max')))
        self.txtYLimMin.setText(to_float(self.config.get('plot.phase.yaxis.min')))
        self.txtYLimMax.setText(to_float(self.config.get('plot.phase.yaxis.max')))

    # ==== SLOTS ====

    @pyqtSlot(bool)
    def on_rbXLimAuto_clicked(self, checked):
        if checked:
            self.config.set('plot.phase.xaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbXLimUser_clicked(self, checked):
        if checked:
            self.config.set('plot.phase.xaxis.limits', 'user')

    @pyqtSlot(bool)
    def on_rbYLimAuto_clicked(self, checked):
        if checked:
            self.config.set('plot.phase.yaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbYLimUser_clicked(self, checked):
        if checked:
            self.config.set('plot.phase.yaxis.limits', 'user')

    @pyqtSlot()
    def on_txtXSteps_editingFinished(self):
        self.int_set('plot.phase.xaxis.steps', self.txtXSteps.text())

    @pyqtSlot()
    def on_txtXLimMin_editingFinished(self):
        self.float_set('plot.phase.xaxis.min', self.txtXLimMin.text())

    @pyqtSlot()
    def on_txtXLimMax_editingFinished(self):
        self.float_set('plot.phase.xaxis.max', self.txtXLimMax.text())

    @pyqtSlot()
    def on_txtYLimMin_editingFinished(self):
        self.float_set('plot.phase.yaxis.min', self.txtYLimMin.text())

    @pyqtSlot()
    def on_txtYLimMax_editingFinished(self):
        self.float_set('plot.phase.yaxis.max', self.txtYLimMax.text())

info = {
    'phase': {
        'description': 'Phase over Wavelength',
        'plotter': PhasePlot,
        'options': PhaseOptions,
    }
}
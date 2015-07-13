#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import baseplot
import numpy as np
from PyQt4.QtCore import pyqtSlot
import matplotlib as mpl

from mixins import XAxisLimits, XAxisSteps
from gui.utils import to_float


class BrownianNoisePlot(baseplot.BasePlot):
    def __init__(self, handle):
        super(BrownianNoisePlot, self).__init__('brownian_noise', handle)

    def brownian_noise(self, coating, freq, beam_size, temperature):
        k = 1.3806503e-23;
        return 2 * k * temperature / (np.sqrt(np.pi ** 3) * freq *
            beam_size * coating.substrate.Y) * (1 - coating.substrate.sigma ** 2) * coating.phi(beam_size)

    def plot(self, coating):
        temperature = self.config.get('analysis.temperature')
        beam_size = self.config.get('analysis.beam_size') * 1e-6
        steps = self.config.get('xaxis.steps')

        if self.config.get('xaxis.limits') == 'auto':
            xlim = [1, 1e4]
            xloglim = [0, 4]
        else:
            xlim = [self.config.get('xaxis.min'),
                    self.config.get('xaxis.max')]
            xloglim = [np.floor(np.log10(xlim[0])),
                       np.ceil(np.log10(xlim[1]))]

        mpl.rc('mathtext', default='regular') #TODO: this should probably go somewhere else?!

        X = np.logspace(*xloglim, num=steps)
        Y = self.brownian_noise(coating, X, beam_size, temperature)

        line = self.handle.loglog(X,np.sqrt(Y))

        self.add_grid()
        self.handle.set_xlim(xlim)

        self.handle.set_xlabel('Frequency (Hz)')
        self.handle.set_ylabel('Displacement noise ($m/\sqrt{Hz}$)')

        self.add_legend(line, ['Brownian Noise'])
        self.add_copyright()


class BrownianNoiseOptions(XAxisSteps, XAxisLimits, baseplot.BasePlotOptionWidget):
    def __init__(self, parent):
        super(BrownianNoiseOptions, self).__init__('brownian_noise', parent)

    def initialise_options(self):
        super(BrownianNoiseOptions, self).initialise_options()
        self.txtTemperature.setText(to_float(self.config.get('analysis.temperature')))
        self.txtBeamSize.setText(to_float(self.config.get('analysis.beam_size')))
        
    # ==== SLOTS ====
    @pyqtSlot()
    def on_txtTemperature_editingFinished(self):
        self.float_set('analysis.temperature', self.txtTemperature.text())

    @pyqtSlot()
    def on_txtBeamSize_editingFinished(self):
        self.float_set('analysis.beam_size', self.txtBeamSize.text())
    

info = {
    'brownian_noise': {
        'description': 'Brownian Noise',
        'plotter': BrownianNoisePlot,
        'options': BrownianNoiseOptions,
    }
}
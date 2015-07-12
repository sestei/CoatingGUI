#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import baseplot
import numpy as np
import matplotlib
from mixins import YAxisLimits, XAxisLimits, YAxisScale, XAxisSteps
from PyQt4.QtCore import pyqtSlot

class R_LambdaPlot(baseplot.BasePlot):
    def __init__(self, handle):
        super(R_LambdaPlot, self).__init__('r_lambda', handle)
        
    def plot(self, coating):
        def to_refl(val, position):
            refl = 1-10**(-val)
            return '{:.7g}'.format(refl)

        yLocator = matplotlib.ticker.MultipleLocator(1.0)
        yFormatter = matplotlib.ticker.FuncFormatter(to_refl)
        
        #TODO: refactor this into another function, which can be used to plot transmission as well
        
        lambda0 = self.config.parent.get('coating.lambda0')
        if self.config.get('xaxis.limits') == 'auto':
            xlim = [0.7 * lambda0, 1.3 * lambda0]
        else:
            xlim = [self.config.get('xaxis.min'),
                    self.config.get('xaxis.max')]
        
        X = np.linspace(*xlim, num=self.config.get('xaxis.steps'))
        Y = np.zeros((len(X), 2))

        AOI = self.config.parent.get('coating.AOI')
        for step in range(len(X)):
            stack = coating.create_stack(X[step], AOI=AOI)
            Y[step,:] = stack.reflectivity(X[step])

        auto_y = self.config.get('yaxis.limits') == 'auto'
        
        if auto_y:
            ylim = [0, 1]
        else:
            ylim = [self.config.get('yaxis.min'),
                    self.config.get('yaxis.max')]
            
        # convert to inverse log scale, i.e. where the values close to unity
        # are zoomed in, instead of the values close to zero
        if self.config.get('yaxis.scale') == 'log':
            Y = -np.log10(1.0-Y)
            if auto_y:
                ylim[0] = 0.3
                ylim[1] = np.ceil(np.max(Y))
            else:
                ylim[0] = -np.log10(1.0-ylim[0])
                ylim[1] = -np.log10(1.0-ylim[1]+1e-6)

        handles = self.handle.plot(X,Y)

        self.add_grid()
        self.handle.set_xlim(xlim)
        self.handle.set_ylim(ylim)
        
        self.handle.axvline(lambda0, ls='--', color=self.colors[4], linewidth=1.5)
        if self.config.get('yaxis.scale') == 'log':
            self.handle.set_yscale('log')
            self.handle.yaxis.set_major_formatter(yFormatter)
            self.handle.yaxis.set_major_locator(yLocator)

        self.handle.set_xlabel('Wavelength (nm)')
        self.handle.set_ylabel('Reflectivity')
        self.add_legend(handles, ['s pol', 'p pol'])
        self.add_copyright()


class R_LambdaOptions(XAxisSteps, XAxisLimits, YAxisLimits, YAxisScale,
                      baseplot.BasePlotOptionWidget):
    def __init__(self, parent):
        super(R_LambdaOptions, self).__init__('r_lambda', parent)

    def initialise_options(self):
        super(R_LambdaOptions, self).initialise_options()
    

info = {
    'r_lambda': {
        'description': 'Reflectivity over Wavelength',
        'plotter': R_LambdaPlot,
        'options': R_LambdaOptions,
    }
}
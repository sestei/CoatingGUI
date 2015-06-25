#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import baseplot
import numpy as np
import matplotlib

class R_lambdaPlot(baseplot.BasePlot):
    def plot(self, coating):
        def to_refl(val, position):
            refl = 1-10**(-val)
            return '{:.7g}'.format(refl)

        yLocator = matplotlib.ticker.MultipleLocator(1.0)
        yFormatter = matplotlib.ticker.FuncFormatter(to_refl)
        
        #TODO: refactor this into another function, which can be used to plot transmission as well
        
        if self.config.get('plot.R_lambda.xaxis.limits') == 'auto':
            lambda0 = self.config.get('coating.lambda0')
            xlim = [0.7 * lambda0, 1.3 * lambda0]
        else:
            xlim = [self.config.get('plot.R_lambda.xaxis.min'),
                    self.config.get('plot.xaxis.max')]
        
        X = np.linspace(*xlim, num=self.config.get('plot.R_lambda.xaxis.steps'))
        Y = np.zeros((len(X), 2))

        AOI = self.config.get('coating.AOI')
        for step in range(len(X)):
            stack = coating.create_stack(X[step], AOI=AOI)
            Y[step,:] = stack.reflectivity(X[step])

        auto_y = self.config.get('plot.R_lambda.yaxis.limits') == 'auto'
        
        ylim = [self.config.get('plot.R_lambda.yaxis.min'),
                self.config.get('plot.R_lambda.yaxis.max')]
        
        if self.config.get('plot.R_lambda.yaxis.scale') == 'log':
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
        
        if self.config.get('plot.R_lambda.yaxis.scale') == 'log':
            self.handle.set_yscale('log')
            self.handle.yaxis.set_major_formatter(yFormatter)
            self.handle.yaxis.set_major_locator(yLocator)

        self.handle.set_xlabel('Wavelength (nm)')
        self.handle.set_ylabel('Reflectivity')
        self.add_legend(handles, ['s pol', 'p pol'])
        self.add_copyright()


class R_lambdaOptions(baseplot.BasePlotOptionWidget):
    def __init__(self, parent):
        super(R_lambdaOptions, self).__init__('R_lambda', parent)

    def initialise_options(self):
        pass


info = {
    'R_lambda': {
        'description': 'Reflectivity over Wavelength',
        'plotter': R_lambdaPlot,
        'options': None,
    }
}
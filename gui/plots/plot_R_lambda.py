#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import baseplot


class R_lambdaPlot(baseplot.BasePlot):
    def plot(self, coating):
        print "plot called"


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
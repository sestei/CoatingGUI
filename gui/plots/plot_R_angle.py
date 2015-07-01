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

class R_AnglePlot(baseplot.BasePlot):
    def plot(self, coating):
        def to_refl(val, position):
            refl = 1-10**(-val)
            return '{:.7g}'.format(refl)

        yLocator = matplotlib.ticker.MultipleLocator(1.0)
        yFormatter = matplotlib.ticker.FuncFormatter(to_refl)
        
        #TODO: refactor this into another function, which can be used to plot transmission as well
        
        AOI = self.config.get('coating.AOI')
        lambda0 = self.config.get('coating.lambda0')

        if self.config.get('plot.R_angle.xaxis.limits') == 'auto':
            xlim = [0.0, min(max(60,AOI+5), 80)]
        else:
            xlim = [self.config.get('plot.R_angle.xaxis.min'),
                    self.config.get('plot.R_angle.xaxis.max')]
        
        X = np.linspace(*xlim, num=self.config.get('plot.R_angle.xaxis.steps'))
        Y = np.zeros((len(X), 2))

        for step in range(len(X)):
            stack = coating.create_stack(lambda0, AOI=X[step])
            Y[step,:] = stack.reflectivity(lambda0)

        auto_y = self.config.get('plot.R_angle.yaxis.limits') == 'auto'
        
        if auto_y:
            ylim = [0, 1]
        else:
            ylim = [self.config.get('plot.R_angle.yaxis.min'),
                    self.config.get('plot.R_angle.yaxis.max')]
        
        # convert to inverse log scale, i.e. where the values close to unity
        # are zoomed in, instead of the values close to zero
        if self.config.get('plot.R_angle.yaxis.scale') == 'log':
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
        
        if self.config.get('plot.R_angle.yaxis.scale') == 'log':
            self.handle.set_yscale('log')
            self.handle.yaxis.set_major_formatter(yFormatter)
            self.handle.yaxis.set_major_locator(yLocator)

        self.handle.set_xlabel('Angle of Incidence (deg)')
        self.handle.set_ylabel('Reflectivity')
        self.add_legend(handles, ['s pol', 'p pol'])
        self.add_copyright()


class R_AngleOptions(baseplot.BasePlotOptionWidget):
    def __init__(self, parent):
        super(R_AngleOptions, self).__init__('R_angle', parent)

    def initialise_options(self):
        if self.config.get('plot.R_angle.xaxis.limits') == 'auto':
            self.rbXLimAuto.setChecked(True)
        else:
            self.rbXLimUser.setChecked(True)

        if self.config.get('plot.R_angle.yaxis.limits') == 'auto':
            self.rbYLimAuto.setChecked(True)
        else:
            self.rbYLimUser.setChecked(True)

        if self.config.get('plot.R_angle.yaxis.scale') == 'lin':
            self.rbYScaleLin.setChecked(True)
        else:
            self.rbYScaleLog.setChecked(True)

        self.txtXSteps.setText(to_float(self.config.get('plot.R_angle.xaxis.steps')))
        self.txtXLimMin.setText(to_float(self.config.get('plot.R_angle.xaxis.min')))
        self.txtXLimMax.setText(to_float(self.config.get('plot.R_angle.xaxis.max')))
        self.txtYLimMin.setText(to_float(self.config.get('plot.R_angle.yaxis.min')))
        self.txtYLimMax.setText(to_float(self.config.get('plot.R_angle.yaxis.max')))

    # ==== SLOTS ====

    @pyqtSlot(bool)
    def on_rbXLimAuto_clicked(self, checked):
        if checked:
            self.config.set('plot.R_angle.xaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbXLimUser_clicked(self, checked):
        if checked:
            self.config.set('plot.R_angle.xaxis.limits', 'user')

    @pyqtSlot(bool)
    def on_rbYLimAuto_clicked(self, checked):
        if checked:
            self.config.set('plot.R_angle.yaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbYLimUser_clicked(self, checked):
        if checked:
            self.config.set('plot.R_angle.yaxis.limits', 'user')

    @pyqtSlot()
    def on_txtXSteps_editingFinished(self):
        self.int_set('plot.R_angle.xaxis.steps', self.txtXSteps.text())

    @pyqtSlot()
    def on_txtXLimMin_editingFinished(self):
        self.float_set('plot.R_angle.xaxis.min', self.txtXLimMin.text())

    @pyqtSlot()
    def on_txtXLimMax_editingFinished(self):
        self.float_set('plot.R_angle.xaxis.max', self.txtXLimMax.text())

    @pyqtSlot()
    def on_txtYLimMin_editingFinished(self):
        self.float_set('plot.R_angle.yaxis.min', self.txtYLimMin.text())

    @pyqtSlot()
    def on_txtYLimMax_editingFinished(self):
        self.float_set('plot.R_angle.yaxis.max', self.txtYLimMax.text())

    @pyqtSlot(bool)
    def on_rbYScaleLin_clicked(self, checked):
        if checked:
            self.config.set('plot.R_angle.yaxis.scale', 'lin')
    
    @pyqtSlot(bool)
    def on_rbYScaleLog_clicked(self, checked):
        if checked:
            self.config.set('plot.R_angle.yaxis.scale', 'log')

info = {
    'R_angle': {
        'description': 'Reflectivity over AOI',
        'plotter': R_AnglePlot,
        'options': R_AngleOptions,
    }
}
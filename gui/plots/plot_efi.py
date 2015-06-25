#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import baseplot
import numpy as np
from PyQt4.QtCore import pyqtSlot
from gui.utils import to_float

class EFIPlot(baseplot.BasePlot):
    @staticmethod
    def get_alpha(n):
        """Converts refractive index n into alpha transparency value"""
        return min(np.log(n)/1.39, 1.0)

    def plot(self, coating):
        wavelength = self.config.get('plot.EFI.analysis.lambda')
        stack = coating.create_stack(wavelength)
        
        # create visual representation of stack
        # and refractive indices
        total_d = np.sum(stack.stacks_d)
        xmin = -0.5 * wavelength / stack.stacks_n[0]
        xmax = total_d + 0.5 * wavelength / stack.stacks_n[-1]
        xvalues = len(stack.stacks_d) * 2 + 4
        X = np.zeros(xvalues)
        Y = np.zeros(xvalues)
        X[0] = xmin; X[1] = -1; X[-1] = xmax; X[-2] = total_d
        Y[0] = Y[1] = stack.stacks_n[0]
        Y[-1] = Y[-2] = stack.stacks_n[-1]
        ii = 1
        current_d = 0
        for d, n in zip(stack.stacks_d, stack.stacks_n[1:-1]):
            X[ii*2] = current_d
            X[ii*2+1] = current_d+d-1
            Y[ii*2] = Y[ii*2+1] = n
            current_d += d
            ii += 1
        self.handle.plot(X,Y, color=self.colors[0])

        # now create EFI plot
        ax2 = self.handle.twinx()
        self.add_grid(ax2)
        ax2.set_ylabel('Normalised Electric Field Intensity')
        if self.config.get('plot.EFI.yaxis.scale') == 'log':
            ax2.set_yscale('log')
        Xefi,Yefi = stack.efi(wavelength)
        ax2.plot(Xefi,Yefi, color=self.colors[1])
        if self.config.get('plot.EFI.yaxis.limits') == 'user':
            ymin = self.config.get('plot.EFI.yaxis.min')
            ymax = self.config.get('plot.EFI.yaxis.max')
            ax2.set_ylim(ymin,ymax)

        # add in colored rectangles to visually indicate
        # layers and their index of refraction
        for ii in range(0, xvalues/2):
            self.handle.axvspan(X[ii*2], X[ii*2+1],
                color=(0.52,0.61,0.73), alpha=EFIPlot.get_alpha(Y[ii*2]))
            if ii == 0:
                text = 'superstrate'
            elif ii == xvalues/2 - 1:
                text = 'substrate'
            else:
                text = '{:.0f}nm'.format(stack.stacks_d[ii-1])
            self.handle.text((X[ii*2]+X[ii*2+1])/2, 0.8, text, 
                horizontalalignment='center', rotation='vertical')

        self.handle.set_xlim(xmin, xmax)
        self.handle.set_ylim(0, np.max(stack.stacks_n)+1)
        self.handle.set_ylabel('Refractive Index')
        self.handle.set_xlabel('Position (nm)')
        self.add_copyright()
       


class EFIPlotOptions(baseplot.BasePlotOptionWidget):
    def __init__(self, parent):
        super(EFIPlotOptions, self).__init__('EFI', parent)

    def initialise_options(self):
        if self.config.get('plot.EFI.yaxis.limits') == 'auto':
            self.rbYLimAuto.setChecked(True)
            self.rbYLimUser.setChecked(False)
        else:
            self.rbYLimAuto.setChecked(False)
            self.rbYLimUser.setChecked(True)
        
        if self.config.get('plot.EFI.yaxis.scale') == 'lin':
            self.rbYScaleLin.setChecked(True)
            self.rbYScaleLog.setChecked(False)
        else:
            self.rbYScaleLin.setChecked(False)
            self.rbYScaleLog.setChecked(True)
        
        self.txtYLimMin.setText(to_float(self.config.get('plot.EFI.yaxis.min')))
        self.txtYLimMax.setText(to_float(self.config.get('plot.EFI.yaxis.max')))

        self.txtSteps.setText(to_float(self.config.get('plot.EFI.analysis.steps')))
        self.txtLambda.setText(to_float(self.config.get('plot.EFI.analysis.lambda')))

    # ==== SLOTS ====

    @pyqtSlot(bool)
    def on_rbYLimAuto_clicked(self, checked):
        if checked:
            self.config.set('plot.EFI.yaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbYLimUser_clicked(self, checked):
        if checked:
            self.config.set('plot.EFI.yaxis.limits', 'user')

    @pyqtSlot()
    def on_txtYLimMin_editingFinished(self):
        self.float_set('plot.EFI.yaxis.min', self.txtYLimMin.text())

    @pyqtSlot()
    def on_txtYLimMax_editingFinished(self):
        self.float_set('plot.EFI.yaxis.max', self.txtYLimMax.text())

    @pyqtSlot()
    def on_txtSteps_editingFinished(self):
        self.int_set('plot.EFI.analysis.steps', self.txtSteps.text())
    
    @pyqtSlot()
    def on_txtLambda_editingFinished(self):
        self.float_set('plot.EFI.analysis.lambda', self.txtLambda.text())
    
    @pyqtSlot(bool)
    def on_rbYScaleLin_clicked(self, checked):
        if checked:
            self.config.set('plot.EFI.yaxis.scale', 'lin')
    
    @pyqtSlot(bool)
    def on_rbYScaleLog_clicked(self, checked):
        if checked:
            self.config.set('plot.EFI.yaxis.scale', 'log')


info = {
    'EFI': {
        'description': 'Electric Field Intensity',
        'plotter': EFIPlot,
        'options': EFIPlotOptions,
    }
}
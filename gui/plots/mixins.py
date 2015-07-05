#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

from PyQt4.QtCore import pyqtSlot
from gui.utils import to_float


class XAxisLimits(object):
    def initialise_options(self):
        if self.config.get('xaxis.limits') == 'auto':
            self.rbXLimAuto.setChecked(True)
        else:
            self.rbXLimUser.setChecked(True)

        self.txtXLimMin.setText(to_float(self.config.get('xaxis.min')))
        self.txtXLimMax.setText(to_float(self.config.get('xaxis.max')))
        
        super(XAxisLimits, self).initialise_options()

    @pyqtSlot(bool)
    def on_rbXLimAuto_clicked(self, checked):
        if checked:
            self.config.set('xaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbXLimUser_clicked(self, checked):
        if checked:
            self.config.set('xaxis.limits', 'user')

    @pyqtSlot()
    def on_txtXLimMin_editingFinished(self):
        self.float_set('xaxis.min', self.txtXLimMin.text())

    @pyqtSlot()
    def on_txtXLimMax_editingFinished(self):
        self.float_set('xaxis.max', self.txtXLimMax.text())


class YAxisLimits(object):
    def initialise_options(self):
        if self.config.get('yaxis.limits') == 'auto':
            self.rbYLimAuto.setChecked(True)
        else:
            self.rbYLimUser.setChecked(True)

        self.txtYLimMin.setText(to_float(self.config.get('yaxis.min')))
        self.txtYLimMax.setText(to_float(self.config.get('yaxis.max')))
        
        super(YAxisLimits, self).initialise_options()

    @pyqtSlot(bool)
    def on_rbYLimAuto_clicked(self, checked):
        if checked:
            self.config.set('yaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbYLimUser_clicked(self, checked):
        if checked:
            self.config.set('yaxis.limits', 'user')

    @pyqtSlot()
    def on_txtYLimMin_editingFinished(self):
        self.float_set('yaxis.min', self.txtYLimMin.text())

    @pyqtSlot()
    def on_txtYLimMax_editingFinished(self):
        self.float_set('yaxis.max', self.txtYLimMax.text())


class YAxisScale(object):
    def initialise_options(self):
        if self.config.get('yaxis.scale') == 'lin':
            self.rbYScaleLin.setChecked(True)
        else:
            self.rbYScaleLog.setChecked(True)

        super(YAxisScale, self).initialise_options()

    @pyqtSlot(bool)
    def on_rbYScaleLin_clicked(self, checked):
        if checked:
            self.config.set('yaxis.scale', 'lin')
    
    @pyqtSlot(bool)
    def on_rbYScaleLog_clicked(self, checked):
        if checked:
            self.config.set('yaxis.scale', 'log')


class XAxisScale(object):
    def initialise_options(self):
        if self.config.get('xaxis.scale') == 'lin':
            self.rbXScaleLin.setChecked(True)
        else:
            self.rbXScaleLog.setChecked(True)

        super(XAxisScale, self).initialise_options()

    @pyqtSlot(bool)
    def on_rbXScaleLin_clicked(self, checked):
        if checked:
            self.config.set('xaxis.scale', 'lin')
    
    @pyqtSlot(bool)
    def on_rbXScaleLog_clicked(self, checked):
        if checked:
            self.config.set('xaxis.scale', 'log')

class XAxisSteps(object):
    def initialise_options(self):
        self.txtXSteps.setText(to_float(self.config.get('xaxis.steps')))

        super(XAxisSteps, self).initialise_options()

    @pyqtSlot()
    def on_txtXSteps_editingFinished(self):
        self.int_set('xaxis.steps', self.txtXSteps.text())


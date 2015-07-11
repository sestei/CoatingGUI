#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from utils import int_conversion_error, float_conversion_error

# actions
WIZARD_BILAYERS = 1
WIZARD_SHIFT = 2

class WizardDialog(QDialog):
    def __init__(self, parent=None):
        super(WizardDialog, self).__init__(parent)
        uic.loadUi('gui/ui_dialogWizard.ui', self)

        # "add bilayers" wizardry
        self.num_bilayers = 2
        self.material1 = ''
        self.material2 = ''
        self.add_hw_cap = False

        # "shift stack" wizardry
        self.shift_percentage = 0

    def load_materials(self, materials):
        materials = sorted([m for m in materials.list_materials()])
        self.cbMaterial1.clear()
        self.cbMaterial2.clear()
        self.cbMaterial1.addItems(materials)
        self.cbMaterial2.addItems(materials)
    
    # ==== SLOTS ====

    @pyqtSlot()
    def on_btnAddBilayers_clicked(self):
        self.done(WIZARD_BILAYERS)

    @pyqtSlot()
    def on_txtNumBilayers_editingFinished(self):
        text = self.txtNumBilayers.text()
        try:
            self.num_bilayers = int(text)
        except ValueError:
            int_conversion_error(text, self)

    @pyqtSlot(str)
    def on_cbMaterial1_currentIndexChanged(self, text):
        self.material1 = str(text)

    @pyqtSlot(str)
    def on_cbMaterial2_currentIndexChanged(self, text):
        self.material2 = str(text)

    @pyqtSlot(bool)
    def on_chkAddCap_toggled(self, state):
        self.add_hw_cap = state

    @pyqtSlot(int)
    def on_sbShiftPercentage_valueChanged(self, value):
        self.shift_percentage = value

    @pyqtSlot()
    def on_btnShift_clicked(self):
        self.done(WIZARD_SHIFT)

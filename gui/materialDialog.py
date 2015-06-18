#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from config import Config
from materials import MaterialLibrary
import math

class UnnamedMaterialException(Exception):
    pass


def get_float(txt, default=0.0):
    val = default
    try:
        val = float(txt)
    except ValueError:
        pass
    return val


class MaterialDialog(QDialog):
    def __init__(self, parent=None):
        super(MaterialDialog, self).__init__(parent)
        uic.loadUi('gui/ui_dialogMaterial.ui', self)
        self.materials = MaterialLibrary.Instance()
        self.old_name = ''

    def load_material(self, material=None):
        if material:
            #TODO: probably directly talk to material classes instead of abusing save()
            mat = self.materials.get_material(material).save()
            self.old_name = material
            self.txtName.setText(material)
            self.txtName.setEnabled(False)
            self.txtNotes.setPlainText(mat['notes'])
            self.load_optical_properties(mat)
            self.load_mechanical_properties(mat)
        else:
            self.txtName.setText('New Material')

    def load_optical_properties(self, mat):
        if mat['B'][1:] == [0.0, 0.0] and mat['C'] == [0.0, 0.0, 0.0]:
            n = math.sqrt(mat['B'][0] + 1.0)
            self.txtRefrIndex.setText(str(n))
            self.rbRefrIndex.setChecked(True)
        else:
            B = map(str, mat['B'])
            C = map(str, mat['C'])
            self.txtB1.setText(B[0])
            self.txtB2.setText(B[1])
            self.txtB3.setText(B[2])
            self.txtC1.setText(C[0])
            self.txtC2.setText(C[1])
            self.txtC3.setText(C[2])
            self.rbSellmeier.setChecked(True)

    def load_mechanical_properties(self, mat):
        pass

    def save_material(self):
        material = str(self.txtName.text()).strip()
        if material=='':
            raise UnnamedMaterialException()
        
        mat = {}
        mat['notes'] = str(self.txtNotes.toPlainText())
        
        mat = self.save_optical_properties(mat)
        mat = self.save_mechanical_properties(mat)
        
        if self.old_name:
            self.materials.unregister(self.old_name)
        self.materials.load_materials({material: mat})
        self.materials.save_material(material)

    def save_optical_properties(self, mat):
        B = [0.0, 0.0, 0.0]
        C = [0.0, 0.0, 0.0]
        if self.rbRefrIndex.isChecked():
            B[0] = get_float(self.txtRefrIndex.text(), 1.0)**2 - 1.0
        else:
            B[0] = get_float(self.txtB1.text())
            B[1] = get_float(self.txtB2.text())
            B[2] = get_float(self.txtB3.text())
            C[0] = get_float(self.txtC1.text())
            C[1] = get_float(self.txtC2.text())
            C[2] = get_float(self.txtC3.text())
        mat['B'] = B
        mat['C'] = C
        return mat

    def save_mechanical_properties(self, mat):
        return mat

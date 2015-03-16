#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from config import Config
from materials import MaterialLibrary

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
            if mat['type'] == 'BaseMaterial':
                self.load_base_material(mat)
            elif mat['type'] == 'OpticalMaterial':
                self.load_optical_material(mat)
            elif mat['type'] == 'MechanicalMaterial':
                self.load_optical_material(mat)
                self.load_mechanical_material(mat)
        else:
            self.txtName.setText('New Material')

    def load_base_material(self, mat):
        self.rbRefrIndex.setChecked(True)
        self.txtRefrIndex.setText(str(mat['n']))

    def load_optical_material(self, mat):
        B = map(str, mat['B'])
        C = map(str, mat['C'])
        self.txtB1.setText(B[0])
        self.txtB2.setText(B[1])
        self.txtB3.setText(B[2])
        self.txtC1.setText(C[0])
        self.txtC2.setText(C[1])
        self.txtC3.setText(C[2])
        self.rbSellmeier.setChecked(True)

    def load_mechanical_material(self, mat):
        pass

    def save_material(self):
        material = str(self.txtName.text()).strip()
        if material=='':
            raise UnnamedMaterialException()
        
        mat = {}
        mat['notes'] = str(self.txtNotes.toPlainText())
        
        if self.rbRefrIndex.isChecked():
            mat = self.save_to_base_material(mat)
        else:
            mat = self.save_to_optical_material(mat)
        #TODO: MechanicalMaterial

        if self.old_name:
            self.materials.unregister(self.old_name)
        self.materials.load_materials({material: mat})
        self.materials.save_material(material)

    def save_to_base_material(self, mat):
        mat['type'] = 'BaseMaterial'
        mat['n'] = get_float(self.txtRefrIndex.text(), 1.0)
        return mat

    def save_to_optical_material(self, mat):
        B = [0.0, 0.0, 0.0]
        C = [0.0, 0.0, 0.0]
        B[0] = get_float(self.txtB1.text())
        B[1] = get_float(self.txtB2.text())
        B[2] = get_float(self.txtB3.text())
        C[0] = get_float(self.txtC1.text())
        C[1] = get_float(self.txtC2.text())
        C[2] = get_float(self.txtC3.text())
        mat['type'] = 'OpticalMaterial'
        mat['B'] = B
        mat['C'] = C
        return mat

    def save_mechanical_material(self, mat):
        pass

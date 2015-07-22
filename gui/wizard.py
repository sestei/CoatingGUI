#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

from utils.config import Config
from dielectric.materials import MaterialLibrary
from wizardDialog import *

class Wizard(QObject):
    def __init__(self, parent):
        self.parent = parent
        self.materials = MaterialLibrary.Instance()
        self.config = Config.Instance()
        super(Wizard, self).__init__()

    def add_bilayers(self, num_bilayers, material1, material2, add_hw_cap):
        m1 = self.materials.get_material(material1)
        m2 = self.materials.get_material(material2)

        lambda0 = self.config.get('coating.lambda0')
        t_qw1 = round(lambda0/(m1.n(lambda0) * 4),1)
        t_qw2 = round(lambda0/(m2.n(lambda0) * 4),1)

        stack = self.config.get('coating.layers')
        if add_hw_cap:
            stack.append([material2, 2*t_qw2])
        for ii in range(num_bilayers):
            stack.append([material1, t_qw1])
            stack.append([material2, t_qw2])

        self.config.set('coating.layers', stack)
        return True

    def shift_stack(self, percentage):
        stack = self.config.get('coating.layers')
        shift = 1.0 + percentage / 100.0
        stack = [[s[0], round(s[1]*shift,1)] for s in stack]
        self.config.set('coating.layers', stack)
        return True

    def run(self):
        dlg = WizardDialog(self.parent)
        dlg.load_materials(self.materials)
        retval = dlg.exec_()
        if retval == WIZARD_BILAYERS:
            return self.add_bilayers(dlg.num_bilayers,
                dlg.material1, dlg.material2, dlg.add_hw_cap)
        elif retval == WIZARD_SHIFT:
            return self.shift_stack(dlg.shift_percentage)
        else:
            return False


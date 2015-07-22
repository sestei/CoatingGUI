#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import numpy as np
from copy import deepcopy
from materials import MaterialLibrary
from stacks import Stack

np.seterr(invalid='raise')

class Coating(object):
    def __init__(self, superstrate, substrate, layers):
        self.superstrate = MaterialLibrary.Instance().get_material(superstrate)
        self.substrate = MaterialLibrary.Instance().get_material(substrate)
        self.layers = [Layer(m, t) for m, t in layers]
        self.update_thickness()

    @staticmethod
    def create_from_config(config):
        MaterialLibrary.Instance().load_materials(config=config)
        superstrate = config.get('coating.superstrate')
        substrate = config.get('coating.substrate')
        layers = config.get('coating.layers')
        return Coating(superstrate, substrate, layers)

    @staticmethod
    def create_from_file(filename):
        from utils.config import Config
        config = Config.Instance()
        config.load(filename)
        return Coating.create_from_config(config)
        
    def create_stack(self, lambda0, AOI=0.0):
        """
        Returns the optical stack for a specific wavelength and AOI.
        """
        stacks_n = np.zeros(len(self.layers)+2)
        stacks_d = np.zeros(len(self.layers))
        stacks_n[0] = self.superstrate.n(lambda0)
        stacks_n[-1] = self.substrate.n(lambda0)
        for ii in range(0, len(self.layers)):
            stacks_n[ii+1] = self.layers[ii].material.n(lambda0)
            stacks_d[ii] = self.layers[ii].thickness
        return Stack(stacks_n, stacks_d, lambda0, AOI)

    def update_thickness(self):
        self.thickness = sum([l.thickness for l in self.layers])
        self.d = self.thickness * 1e-9

    def add_layers(self, layers, wavelength, repeat=1):
        """
        Adds the given layers (a list of material/thickness pairs)
        to the stack. Thickness is interpreted as optical thickness
        given as a fraction of the wavelength, i.e. a thickness of 0.25
        would result in a quarter-wave layer.
        """
        new_layers = [Layer(m, t) for m, t in layers]
        for ll in new_layers:
            ll.thickness = ll.thickness * wavelength / ll.material.n(wavelength)
        self.add_layers_direct(new_layers, repeat)

    def add_layers_direct(self, layers, repeat=1):
        """
        Adds the given layers (a list of Layer instances) to the stack.
        """
        mylayers = [deepcopy(l) for l in layers*repeat]
        self.layers.extend(mylayers)
        self.update_thickness()

    def yPara(self):
        """Total parallel Young's modulus."""
        return 1/self.d * sum([l.d * l.material.Y for l in self.layers])

    def yPerp(self):
        """Total perpendicular Young's modulus."""
        return self.d / sum([l.d / l.material.Y for l in self.layers])

    def phiPara(self):
        """Total parallel loss angle."""
        return 1 / (self.d * self.yPara()) * sum([l.material.Y * l.material.phi * l.d for l in self.layers])

    def phiPerp(self):
        """Total perpendicular loss angle."""
        return self.yPerp() / self.d * sum([l.d * l.material.phi / l.material.Y for l in self.layers])

    def sigmaPara(self):
        """Total stack parallel Poisson's ratio."""
        return np.mean([l.material.sigma for l in self.layers])

    def sigmaPerp(self):
        """Total perpendicular Poisson's ratio."""
        return sum([l.material.sigma * l.material.Y * l.d for l in self.layers]) / sum([l.material.Y * l.d for l in self.layers])

    def phi(self, beam_size):
        """Effective loss angle."""
        return (self.d / (np.sqrt(np.pi) * beam_size * self.yPerp()) *
            (self.phiPerp() *
             (self.substrate.Y / (1 - self.substrate.sigma ** 2) -
              2 * self.sigmaPerp() ** 2 * self.substrate.Y * self.yPara() /
              (self.yPerp() * (1 - self.substrate.sigma ** 2) * (1 - self.sigmaPara()))) +
             self.yPara() * self.sigmaPerp() * (1 - 2 * self.substrate.sigma) /
             ((1 - self.sigmaPara()) * (1 - self.substrate.sigma)) *
             (self.phiPara() - self.phiPerp()) +
             self.yPara() * self.yPerp() * (1 + self.substrate.sigma) *
             (self.phiPara() * (1 - 2 * self.substrate.sigma) ** 2) /
             (self.substrate.Y * (1 - self.sigmaPara() ** 2) * (1 - self.substrate.sigma))))

    def R(self, lambda0, AOI=0.0):
        """
        Convenience function that returns a tuple with s and p pol
        reflectivity of the coating at wavelength lambda0 and angle
        of incidence AOI.
        """
        stack = self.create_stack(lambda0, AOI)
        return stack.reflectivity()

    def Rs(self, lambda0, AOI=0.0):
        return self.R(lambda0, AOI)[0]

    def Rp(self, lambda0, AOI=0.0):
        return self.R(lambda0, AOI)[1]


class Layer(object):
    def __init__(self, material, thickness):
        self.material = MaterialLibrary.Instance().get_material(material)
        self.thickness = thickness

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        self._d = value * 1e-9



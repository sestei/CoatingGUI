#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import numpy as np
from materials import MaterialLibrary
from dielectric.stacks import Stack

np.seterr(invalid='raise')

class Coating(object):
    def __init__(self, superstrate, substrate, layers):
        self.superstrate = MaterialLibrary.Instance().get_material(superstrate)
        self.substrate = MaterialLibrary.Instance().get_material(substrate)
        self.layers = [Layer(m, t) for m, t in layers]
        self.thickness = sum([l.thickness for l in self.layers])
        self.d = self.thickness * 1e-9
        
    def create_stack(self, lambda0, AOI=0.0):
        """
        Returns an optical stack for a specific wavelength and AOI.
        """
        stacks_n = np.zeros(len(self.layers)+2)
        stacks_d = np.zeros(len(self.layers))
        stacks_n[0] = self.superstrate.n(lambda0)
        stacks_n[-1] = self.substrate.n(lambda0)
        for ii in range(0, len(self.layers)):
            stacks_n[ii+1] = self.layers[ii].material.n(lambda0)
            stacks_d[ii] = self.layers[ii].thickness
        return Stack(stacks_n, stacks_d, AOI)

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

class Layer(object):
    def __init__(self, material, thickness):
        self.material = MaterialLibrary.Instance().get_material(material)
        self.thickness = thickness
        self.d = self.thickness * 1e-9


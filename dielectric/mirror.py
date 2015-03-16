#!/usr/bin/python

import stacks
import numpy as np
import unittest

def X_wave(X, n, wavelength):
    """
    Returns the thickness of a material with refractive index n which
    is a X*lambda layer
    """
    return X*wavelength / n

class Mirror(object):
    """Basic mirror"""
    def __init__(self, n_subs = 1.46, n_air = 1.0, wavelength=1.0):
        self.wavelength = wavelength
        self.stack = stacks.Stack([n_air, n_subs], []) 

    def add_layers(self, n, do, wavelength=-1, repeat=1):
        """
        Add repeat layers/stacks with refractive indices n, optical thickness do (in terms of the
        wavelength, e.g. 0.5 is a half-wave layer for that wavelength)
        """
        n = np.tile(np.array(n, ndmin=1), repeat)
        do = np.tile(np.array(do, ndmin=1), repeat)
        if wavelength < 0.0:
            wavelength = self.wavelength

        d = X_wave(do, n, wavelength)

        self.add_layers_direct(n, d, 1)

    def add_layers_direct(self, n, d, repeat=1):
        """
        Add repeat layers/stacks with refractive indices n, geometric
        thickness d
        """
        n = np.tile(np.array(n, ndmin=1), repeat)
        d = np.tile(np.array(d, ndmin=1), repeat)

        stack_n = self.stack.stacks_n
        stack_d = self.stack.stacks_d

        self.stack.stacks_n = np.insert(stack_n, -1, n)
        self.stack.stacks_d = np.append(stack_d, d)

    def get_reflectivity(self, wavelength=-1, AOI=0.0):
        if wavelength < 0.0:
            wavelength = self.wavelength
        self.stack.alpha_0 = AOI
        return self.stack.reflectivity(wavelength)

    def R(self, wavelength=-1, AOI=0.0):
        return self.get_reflectivity(wavelength, AOI)

    def T(self, wavelength=-1, AOI=0.0):
        rs, rp = self.get_reflectivity(wavelength, AOI)
        return (1-rs, 1-rp)

#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

#
# Optimiser:
# should live in utils, should already implement call to fmin etc.,
# and update the thickness of the layers in a coating. Should require
# a FOM function that needs to be minimised, as well as an initial coating
# (defining the number of layers and the materials)

import numpy as np
from dielectric import coating
from scipy.optimize import fmin


class OptimiseException(Exception):
    pass


def coating_updater(coating, d):
    coating.adjust_layers(d)


def optimiser_run(coating, FOM, d):
    if np.any(d > coating.lambda0) or np.any(d < 1):
        return np.inf
    coating_updater(coating, d)
    return FOM(coating)


def optimise(coating, FOM, ftol=0.5, maxiter=1000):
    if coating.lambda0 == 0.0:
        raise OptimiseException('Please set coating.lambda0 before using optimise().')
    stack = coating.create_stack()  # TODO: add AOI
    initial_d = stack.stacks_d
    result = fmin(lambda d: optimiser_run(coating, FOM, d),
                 initial_d, maxiter=maxiter, disp=True, ftol=ftol, full_output=True)
    coating_updater(coating, result[0])
    return coating

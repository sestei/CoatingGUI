#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import numpy as np
import mirror
from pylab import *

from scipy.optimize import fmin

def stack_updater(stack, d):
    stack.stacks_d = d
    stack.update()

def FOM(stack):
    r532 = 0
    for ii in range(-20,20,5):
        r532 += stack.reflectivity(532+ii)[0]
    t1064 = 0
    for ii in range(-20,20,5):
        t1064 += 1-stack.reflectivity(1064+ii)[0]
    return np.sqrt((4*t1064)**2+r532**2) # t1064 is weighted higher

def optimizer(stack, d):
    if np.any(d > 1000) or np.any(d < 0):
        return np.inf
    stack_updater(stack, d)
    return FOM(stack)

m = mirror.Mirror(wavelength=1064, n_subs=1.52)
n = [1.45,2.35]
d = [0.5, 0.25]
m.add_layers(n, d) # half-wave cap
d = [0.25, 0.25]
m.add_layers(n, d, repeat=9)
#d = [364,114,181,113,181,113,178,112,178,115,178,111,173,108,196,129]
#m.add_layers_direct(n, d)
rs1064,_ = m.get_reflectivity(1064)
rs532,_ = m.get_reflectivity(532)
print "R @ 1064nm: {:.4%}, T @ 532nm: {:.4%}".format(rs1064, 1-rs532)
print FOM(m.stack)

L = linspace(400,1200,300)
R_preopt = zeros_like(L)
for ii in range(0, len(L)):
    R_preopt[ii] = m.R(L[ii])[0]

opt_d = fmin(lambda x: optimizer(m.stack, x), m.stack.stacks_d, maxiter=5000, disp=True, ftol=0.5)
#stack_updater(m.stack, [364,114,181,113,181,113,178,112,178,115,178,111,173,108,196,129])
stack_updater(m.stack, opt_d)
rs1064,_ = m.get_reflectivity(1064)
rs532,_ = m.get_reflectivity(532)
print "R @ 1064nm: {:.4%}, T @ 532nm: {:.4%}".format(rs1064, 1-rs532)
print FOM(m.stack)

R_opt = zeros_like(L)
for ii in range(0, len(L)):
    R_opt[ii] = m.R(L[ii])[0]

plot(L, R_preopt, L, R_opt)
show()
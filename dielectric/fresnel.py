#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import numpy as np

def angle(alpha1, n1, n2):
    """
    Returns the angle after refraction at a boundary with indices of refraction
    n1 and n2, angle of incidence alpha1
    """
    return np.arcsin(n1/n2 * np.sin(alpha1))

def rho(alpha1, n1, alpha2, n2):
    """
    Returns a pair of reflectivities for a boundary between materials of
    refractive indices n1 and n2, with angles of incidence alpha1 and alpha2
    """
    a = n1*np.cos(alpha1)
    b = n2*np.cos(alpha2)
    c = n2*np.cos(alpha1)
    d = n1*np.cos(alpha2)
    rho_s = (a-b)/(a+b)
    rho_p = (c-d)/(c+d)
    return (rho_s, rho_p)

#!/usr/bin/python
import stacks
import numpy as np

class StackBuilderException(Exception):
    pass

def quarter_wave(n, alpha, wavelength):
    """
    Returns the thickness of a material with refractive index n which
    is a lambda/4 layer for a wave at angle alpha
    """
    return X_wave(1/4.0, n, alpha, wavelength)

def half_wave(n, alpha, wavelength):
    """
    Returns the thickness of a material with refractive index n which
    is a lambda/2 layer for a wave at angle alpha
    """
    return X_wave(1/2.0, n, alpha, wavelength)

def X_wave(X, n, alpha, wavelength):
    """
    Returns the thickness of a material with refractive index n which
    is a X*lambda layer for a wave at angle alpha
    """
    return X*wavelength / (np.cos(alpha) * n)


def quarter_wave_stack(num_stacks, n_stack, n_air_subs, wavelength = 1.0):
    if len(n_stack) != 2:
        raise StackBuilerException('only exactly two materials supported')
    stacks_n = [n_air_subs[0]] + list(n_stack)*num_stacks + [n_air_subs[1]]
    stacks_n = np.asarray(stacks_n)
    stacks_d = quarter_wave(stacks_n[1:-1], 0.0, wavelength)
    return stacks.Stack(stacks_n, stacks_d)

def capped_quarter_wave_stack(num_stacks, n_stack, n_air_subs, n_cap, wavelength = 1.0):
    if len(n_stack) != 2:
        raise StackBuilerException('only exactly two materials supported')
    stacks_n = [n_air_subs[0], n_cap] + list(n_stack)*num_stacks + [n_air_subs[1]]
    stacks_n = np.asarray(stacks_n)
    stacks_d = quarter_wave(stacks_n[1:-1], 0.0, wavelength)
    stacks_d[0] = half_wave(stacks_n[1], 0.0, wavelength)
    return stacks.Stack(stacks_n, stacks_d)



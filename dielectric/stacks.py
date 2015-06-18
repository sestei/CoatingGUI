#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

from itertools import izip
import numpy as np
import fresnel

class StackException(Exception):
    pass        

def delta(d, n, alpha, wavelength):
    """
    Returns the additional phase for propagating a distance d
    with index of refraction n
    """
    k = n*2*np.pi/wavelength
    return k*d * np.cos(alpha) #TODO unsolved question: should this be "*" or "/"???

def M(rho, delta):
    """
    Returns the transfer matrix for a mirror surface with
    amplitude reflectivity rho, followed by a propagation phase delta
    """
    tau = np.sqrt(1-rho**2)
    return 1/tau * (np.matrix([[1, rho], [rho, 1]])
                    * np.matrix([[np.exp(-1j*delta), 0], [0, np.exp(1j*delta)]]))

class Stack(object):
    """docstring for Stack"""
    def __init__(self, stacks_n, stacks_d, alpha_0=0.0):
        self._layers = len(stacks_n)

        self._stacks_n = np.asarray(stacks_n)
        self._stacks_d = np.asarray(stacks_d)
        self._alpha_0 = np.deg2rad(alpha_0)
        self._stacks_rho = np.zeros(self._layers-1)
        self._stacks_a = np.zeros(self._layers-1)
        self._valid = False
        self._angles_valid = False
    
    def is_valid(self):
        return self._valid and self._angles_valid

    def update(self):
        if self.is_valid():
            return # nothing to do
        if not self._angles_valid:
            self._update_angles()
        self._update_rhos()

    def _update_angles(self):
        """
        Returns the angles at which a light wave propagates inside each layer of
        a multi-layer stack, given by the indices of refraction stacks_n and
        initial angle of incidence alpha
        """
        if self._alpha_0 == 0:
            self._stacks_a = np.zeros(self._layers-1)
        else:
            # this works because at each boundary, the refractive index of the first medium
            # together with the angle of incidence are actually the same as the incoming beam's
            # angle of incidence, in air
            self._stacks_a = fresnel.angle(self._alpha_0, self._stacks_n[0], self._stacks_n[1:])
        self._angles_valid = True

    def _update_rhos(self):
        """
        Returns the reflectivities at a boundary of stacks with
        reflectivities stacks_n and angles of incidence stacks_a
        """
        n = self._stacks_n[0] 
        a = self._alpha_0
        rhos = []
        for n2, a2 in zip(self._stacks_n[1:], self._stacks_a):
            rhos.append(fresnel.rho(a, n, a2, n2))
            a = a2
            n = n2
        self._stacks_rho = np.array(rhos)
        self._valid = True

    def _propagate(self, wavelength):
        if not self.is_valid():
            self.update()
        Ms = np.eye(2)
        Mp = np.eye(2)
        deltas = np.zeros(len(self._stacks_rho))
        deltas[0:-1] = delta(self._stacks_d,
                           self._stacks_n[1:-1],
                           self._stacks_a[0:-1],
                           wavelength)
        for r, p in zip(self._stacks_rho, deltas):
            Ms = Ms * M(r[0], p)
            Mp = Mp * M(r[1], p)

        return Ms, Mp

    def efi(self, wavelength, steps=30):
        # EFI calculation following Arnon/Baumeister 1980
        # TODO: this needs to be combined with the above calculation, can't be
        #       that difficult!
        # TODO: AOI is not taken into account for now, as well as s/p distinction

        def M_i(beta_i, q_i):
            return np.matrix([[np.cos(beta_i), 1j/q_i * np.sin(beta_i)],
                              [1j*q_i*np.sin(beta_i), np.cos(beta_i)]])

        def beta_i(theta_i, n_i, h_i):
            return 2*np.pi/wavelength*np.cos(theta_i)*n_i*h_i

        def q_i(n_i):
            return n_i # for now, but see (5) and (6) of Arnon/Baumeister 1980
                       # for non-normal incidence

        def _M():
            myM = np.eye(2)
            for n_i, h_i in izip(self._stacks_n[1:-1], self._stacks_d):
                myM = myM * M_i(beta_i(0.0, n_i, h_i), q_i(n_i))
            return myM

        def E0p2(myM):  # (10) 
            q0 = q_i(self._stacks_n[0])
            qs = q_i(self._stacks_n[-1])
            # possibly need 1j*m12 etc. here?
            return 0.25*( abs(myM[0,0]+myM[1,1]*qs/q0)**2 
                         +abs(myM[1,0]/q0 + myM[0,1] * qs)**2 )

        def deltaM(beta_i, q_i): # (11)
            return M_i(beta_i, -q_i)

        X = np.zeros(steps*self._layers)
        E2 = np.zeros(steps*self._layers)
        curX = 0.0
        myM = _M()
        myMz = myM
        qs = q_i(self._stacks_n[-1])
        # propagate through stack, where steps is the number of points
        # calculated for each layer
        for ii in range(0, self._layers):
            n_i = self._stacks_n[ii]
            if ii == 0:
                deltaL = -wavelength / 2.0 / n_i / steps
            elif ii == self._layers-1:
                deltaL = wavelength / 2.0 / n_i / steps
            else:
                deltaL = self._stacks_d[ii-1] / steps
            
            for jj in range(0, steps):
                curX += deltaL
                X[ii*steps + jj] = curX
                myMz = deltaM(beta_i(0.0, n_i, deltaL), q_i(n_i)) * myMz # (13)
                E2[ii*steps + jj] = abs(myMz[0,0])**2 + abs(qs/1j*myMz[0,1])**2 # (14)

            if ii == 0:
                myMz = myM # reset matrix after superstrate calculations as we're now
                           # going in the other direction, into the coating
                curX = 0.0

        X[0:steps] = X[steps-1::-1] # reverse first elements
        E2[0:steps] = E2[steps-1::-1]

        return (X, E2/E0p2(myM))

    def reflectivity(self, wavelength):
        Ms, Mp = self._propagate(wavelength)

        rs = abs(Ms[1,0] / Ms[0,0])
        rp = abs(Mp[1,0] / Mp[0,0])
        return (rs**2, rp**2)

    def phase(self, wavelength):
        Ms, Mp = self._propagate(wavelength)

        phis = -np.angle(Ms[1,0] / Ms[0,0])
        phip = -np.angle(Mp[1,0] / Mp[0,0])
        return phis, phip+np.pi, phip-phis

    def alpha_0():
        doc = "The alpha_0 property."
        def fget(self):
            return np.rad2deg(self._alpha_0)
        def fset(self, value):
            if not 0 <= value < 90:
                raise StackException('alpha_0 not in range 0..90 degrees')
            self._alpha_0 = np.deg2rad(value)
            self._angles_valid = False
        return locals()
    alpha_0 = property(**alpha_0())

    def stacks_n():
        doc = "The stacks_n property."
        def fget(self):
            return self._stacks_n
        def fset(self, value):
            self._stacks_n = np.array(value)
            self._layers = len(self._stacks_n)
            self._valid = False
        return locals()
    stacks_n = property(**stacks_n())

    def stacks_d():
        doc = "The stacks_d property."
        def fget(self):
            return self._stacks_d
        def fset(self, value):
            self._stacks_d = np.array(value)
        return locals()
    stacks_d = property(**stacks_d())

    @property
    def stacks_rho(self):
        return self._stacks_rho


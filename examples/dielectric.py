#!/usr/bin/python

from pylab import *
import nelder_mead as nm
import pdb

def angle(alpha1, n1, n2):
    """
    Returns the angle after refraction at a boundary with indices of refraction
    n1 and n2, angle of incidence alpha1
    """
    return arcsin(n1/n2 * sin(alpha1))

def get_alphas(stacks_n, alpha):
    """
    Returns the angles at which a light wave propagates inside each layer of
    a multi-layer stack, given by the indices of refraction stacks_n and
    initial angle of incidence alpha
    """
    # this works because at each boundary, the refractive index of the first medium
    # together with the angle of incidence are actually the same as the incoming beam's
    # angle of incidence, in air
    return arcsin(stacks_n[0] / array(stacks_n) * sin(alpha))

def rho(alpha1, n1, alpha2, n2):
    """
    Returns a pair of reflectivities for a boundary between materials of
    refractive indices n1 and n2, with angles of incidence alpha1 and alpha2
    """
    a = n1*cos(alpha1)
    b = n2*cos(alpha2)
    c = n2*cos(alpha1)
    d = n1*cos(alpha2)
    rho_s = (a-b)/(a+b)
    rho_p = (c-d)/(c+d)
    return (rho_s, rho_p)

def get_rhos(stacks_n, stacks_a):
    """
    Returns the reflectivities at a boundary of stacks with
    reflectivities stacks_n and angles of incidence stacks_a
    """
    n = stacks_n[0] 
    a = stacks_a[0]
    rhos = []
    for n2, a2 in zip(stacks_n, stacks_a):
        rhos.append(rho(a, n, a2, n2))
        a = a2
        n = n2
    return array(rhos)

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
    return X*wavelength / (cos(alpha) * n)
    
def M(rho, delta):
    """
    Returns the transfer matrix for a mirror surface with
    amplitude reflectivity rho, followed by a propagation phase delta
    """
    tau = sqrt(1-rho**2)
    return 1/tau * matrix([[1, rho], [rho, 1]]) * matrix([[exp(-1j*delta), 0], [0, exp(1j*delta)]])

def delta(d, n, alpha, wavelength):
    """
    Returns the additional phase for propagating a distance d
    with index of refraction n
    """
    k = n*2*pi/wavelength
    return k*d * cos(alpha)

def calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength):
    Ms = eye(2)
    Mp = eye(2)
    deltas = delta(stacks_d, stacks_n, stacks_a, wavelength)
    for r, p in zip(stacks_rho, deltas):
        Ms = Ms * M(r[0], p)
        Mp = Mp * M(r[1], p)

    rs = abs(Ms[1,0] / Ms[0,0])
    rp = abs(Mp[1,0] / Mp[0,0])
    return (rs, rp)


def example_interference_filter():
    """
    Simulates small cavity acting as a narrowband interference filter
    """
    wavelength = 1000
    alpha_0 = 0.0
    n_sio = 1.45
    n_ta = 2.35
    
    # BK7 | two QW stacks | air gap | two QW stacks | BK7
    stacks_n = array([1.52] + [n_sio, n_ta] * 2 + [1.0] + [n_ta, n_sio]*2 + [1.52])
    stacks_a = get_alphas(stacks_n, alpha_0)
    qws = quarter_wave(array([n_sio, n_ta]), 0.0, wavelength);
    stacks_d = hstack(([0.0], qws, qws, 1e5, qws[::-1], qws[::-1], [0]))
    stacks_rho = get_rhos(stacks_n, stacks_a)

    x = linspace(990, 1010, 500)
    ys = zeros_like(x)
    yp = zeros_like(x)
    ii = 0
    for l in x:
        R = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, l)
        ys[ii] = 1-R[0]**2
        yp[ii] = 1-R[1]**2
        ii += 1
        
    figure()
    plot(x, ys*100, x, yp*100)
    ylabel('Transmission (%)')
    xlabel('Wavelength (nm)')
    title('example_interference_filter')
    show()

def example_808_1064_dichroic():
    """
    Example for a dichroic mirror HR@1064nm, HT@808nm, taken from rpphotonics website

    Note that currently we haven't implemented a wavelength-dependent refractive index,
    so the results are increasingly incorrect especially towards small wavelengths.
    """
    n_sio = 1.45
    n_ta = 2.35

    stacks_n = array([1.0,n_sio] + [n_ta, n_sio]*8)
    stacks_n[-1] = 1.52
    stacks_a = get_alphas(stacks_n, 0.0)
    stacks_rho = get_rhos(stacks_n, stacks_a)
    stacks_d = array([0,364,114,181,113,181,113,178,112,178,115,178,111,173,108,196,129,0])

    rhr = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, 1064)[0]
    rht = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, 808)[0]
    print "R @ 1064nm : %.3f%%, R @ 808nm: %.3f%%" % (rhr**2 * 100, rht**2 * 100)

    x = linspace(600, 1400, 500)
    ys = zeros_like(x)
    yp = zeros_like(x)
    ii = 0
    for l in x:
        R = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, l)
        ys[ii] = R[0]**2
        yp[ii] = R[1]**2
        ii += 1
        
    figure()
    plot(x, ys*100, x, yp*100)
    ylabel('Reflection (%)')
    xlabel('Wavelength (nm)')
    title('example_808_1064_dichroic')
    show()

def example_deviation_from_qws():
    """
    Example showing reflectivity changes when going from a quarter-wave stack to
    something like 3/8 + 1/8.
    """
    alpha_0 = 0
    n_sio = 1.45
    n_ta = 2.35
    wavelength = 1

    stacks_n = array([1.0] + [n_sio] + [n_ta, n_sio]*6)
    stacks_a = get_alphas(stacks_n, alpha_0)
    stacks_rho = get_rhos(stacks_n, stacks_a)
    stacks_d = quarter_wave(stacks_n, alpha_0, wavelength)    
    stacks_d[1] = half_wave(n_sio, alpha_0, wavelength) # l/2 layer of SiO at the top
    stacks_d[0] = stacks_d[-1] = 0.0 # reset substrate and air thickness

    # indices for the tantala and silica layers
    ii_ta = arange(int((len(stacks_n)-2)/2))*2 + 2
    ii_sio = ii_ta + 1
    
    x = linspace(0.2,0.8,500)
    y = zeros_like(x)
    ii = 0
    for X in x:
        stacks_d[ii_ta] = X_wave(1/2.0 * X, n_ta, alpha_0, wavelength)        
        stacks_d[ii_sio] = X_wave(1/2.0 * (1-X), n_sio, alpha_0, wavelength)        
        y[ii] = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)[0]
        ii += 1

    figure()
    plot(x, y**2 * 100)
    ylabel('Reflection (%)')
    xlabel('Fill factor')
    title('example_deviation_from_qws')
    show()


def create_stack(num_stacks, wavelength = 1.0, alpha_0 = 0.0, n_layers = [1.45, 2.35], n_substrate = 2.35):
    stacks_n = array([1.0] + n_layers*num_stacks + [n_layers[0]]);
    stacks_a = get_alphas(stacks_n, alpha_0)
    stacks_d = quarter_wave(stacks_n, stacks_a, wavelength)
    stacks_d[1] = half_wave(n_layers[0], stacks_a[1], wavelength)
    stacks_d[0] = stacks_d[-1] = 0.0

    return (stacks_n, stacks_d, stacks_a)

def FOM(x, design_trans, bounds, stacks_rho, stacks_a, stacks_d, stacks_n, wavelength):
    """
    Calculate a figure of merit, which here is simply the squared difference between
    actual and designed transmission, in ppm**2
    """
    if any(x < bounds[0]):
        return inf
    elif any(x > bounds[1]):
        return inf

    stacks_d[-3:-1] = x
    rho = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)[0]
    T = (1-rho**2)
    return ((T - design_trans)*1e6)**2

def hr_mirror(design_refl, alpha_0 = 0.0, n_layers = [1.45, 2.35], n_substrate = 2.35):
    """
    Return stack for required design reflectivity
    """
    n_layers.sort()

    wavelength = 1.0

    actual_refl = 0.0
    num_stacks = 0
    while actual_refl < design_refl:
        num_stacks += 1
        if num_stacks > 50:
            raise Exception("Maximum number of stacks exceeded")

        stacks_n, stacks_d, stacks_a = create_stack(num_stacks, wavelength, alpha_0, n_layers, n_substrate)
        stacks_rho = get_rhos(stacks_n, stacks_a);

        rho = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)[0]
        actual_refl = rho**2
        #pdb.set_trace()
        print "%d stacks: delta_R = %f, %f" % (num_stacks, design_refl-actual_refl, actual_refl)

    print "Found minimum number of stacks, now fine-tuning..."

    # layers should at maximum be a half-wave stack
    bounds = [zeros_like(n_layers),
              array(half_wave(array(n_layers), alpha_0, wavelength))]
    # calculate starting point somewhere in between
    S = nm.regular_simplex(len(n_layers))
    origin = (bounds[1]-bounds[0])/2.0
    scale = np.minimum(bounds[1]-origin, origin-bounds[0]) * 0.75
    S = S*scale + origin

    # define figure of merit
    myFOM = lambda x: FOM(x, (1-design_refl), bounds,
                          stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)

    res = nm.run(myFOM, S, 10000, 1e-6)
    print "done."

    stacks_d[-3:-1] = res[0]
    return (stacks_n, stacks_d)

def hr_1064_1000ppm():
    """
    Example for automatically designing an HR mirror w/ 1000ppm transmission
    """
    alpha_0 = deg2rad(30.0)
    wavelength = 1064e-9
    design_refl = 0.995

    stacks_n, stacks_d = hr_mirror(design_refl, alpha_0)
    stacks_d *= wavelength
    stacks_a = get_alphas(stacks_n, alpha_0)
    stacks_rho = get_rhos(stacks_n, stacks_a)
    rho = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)[0]

    actual_refl = rho**2
    print "R: %f, delta_R = %f" % (actual_refl, design_refl-actual_refl)
    print "Here's the stack (in nm):"
    print stacks_d * 1e9

    ii = 0
    r_s = zeros(100)
    r_p = zeros(100)
    angles = linspace(0, 50, 100)
    for aa in angles:
        alpha_0 = deg2rad(aa)
        stacks_a = get_alphas(stacks_n, alpha_0)
        stacks_rho = get_rhos(stacks_n, stacks_a)
        rho = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)
        #print "Rs: %f, Rp: %f" % (rho[0]**2, rho[1]**2)
        r_s[ii] = rho[0]**2
        r_p[ii] = rho[1]**2
        ii += 1

    plot(angles, r_s*100, angles, r_p*100)
    ylim([99., 100.0])
    grid('on')
    yticks(linspace(99., 100.0, 11))
    show()

def hr_1064_alpha():
    """
    As above, but with fixed layers for now to test against Sean's calculations
    """

    alpha_design = deg2rad(30.0)
    wavelength = 1

    n_layers = 14
    stacks_n = array([1.0] + [1.44962,2.06]*n_layers + [1.44962])
    stacks_a = get_alphas(stacks_n, alpha_design)
    stacks_d = quarter_wave(stacks_n, stacks_a, wavelength)
    stacks_d[1] = half_wave(stacks_n[1], stacks_a[1], wavelength)
    stacks_d[0] = stacks_d[-1] = 0.0

    stacks_rho = get_rhos(stacks_n, stacks_a)
    rho = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)
    print "Rs: %f, Rp: %f" % (rho[0]**2, rho[1]**2)

    ii = 0
    r_s = zeros(100)
    r_p = zeros(100)
    angles = linspace(0, 50, 100)
    for aa in angles:
        alpha_0 = deg2rad(aa)
        stacks_a = get_alphas(stacks_n, alpha_0)
        stacks_rho = get_rhos(stacks_n, stacks_a)
        rho = calc_refl(stacks_rho, stacks_a, stacks_d, stacks_n, wavelength)
        #print "Rs: %f, Rp: %f" % (rho[0]**2, rho[1]**2)
        r_s[ii] = rho[0]**2
        r_p[ii] = rho[1]**2
        ii += 1

    plot(angles, r_s*100, angles, r_p*100)
    ylim([99.9, 100.0])
    grid('on')
    yticks(linspace(99.9, 100.0, 11))
    show()


if __name__ == "__main__":
    close('all')    
    
    #example_deviation_from_qws()
    #example_808_1064_dichroic()
    #example_interference_filter()

    hr_1064_1000ppm()

    #hr_1064_alpha()

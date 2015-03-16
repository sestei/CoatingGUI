#!/usr/bin/python

import mirror
from pylab import *

m = mirror.Mirror(wavelength=1064, n_subs=1.45)
n = [2.2, 1.45]
d = [0.25, 0.25]
m.add_layers(n[1], 0.5) # half-wave cap
m.add_layers(n, d, repeat=15) # quarter-wave stacks
m.add_layers(n[0], 0.25)

rs, rp = m.get_reflectivity(1064)
print "\tR @ 1064nm: {:.4%}".format(rs)
print "num layers: {:}, thickness: {:.3f}".format(len(m.stack.stacks_d), np.sum(m.stack.stacks_d))

m = mirror.Mirror(wavelength=1064, n_subs=1.45)
n = [2.2, 1.45]
d = [0.25, 0.25]
n2 = [1.45, 3.5]
m.add_layers(n[1], 0.5) # half-wave cap
m.add_layers(n, d, repeat=5) # quarter-wave stacks
m.add_layers(n[0], 0.25)
rs, rp = m.get_reflectivity(1064)
print "\tT SiO-Tantala @ 1064nm: {:.4%}".format(1-rs)
m.add_layers(n2, d, repeat=5)

rs, rp = m.get_reflectivity(1064)
print "\tR @ 1064nm: {:.4%}".format(rs)

print "num layers: {:}, thickness: {:.3f}".format(len(m.stack.stacks_d), np.sum(m.stack.stacks_d))

#ll = linspace(900,1280,500)
#rr = zeros_like(ll)
#ii = 0
#for L in ll:
#    rr[ii] = m.get_reflectivity(L)[0]
#    ii += 1
#
#plot(ll, rr)
#xlim((ll[0],ll[-1]))
#ylabel('reflectivity')
#xlabel('wavelength')
#show()

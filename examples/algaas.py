#!/usr/bin/python

import mirror
from pylab import *

m = mirror.Mirror(wavelength=1083, n_subs=1.45)
n = [3.48041, 2.97717]
d = [77.3598, 91.4549]
m.add_layers_direct(n, d, repeat=40)
m.add_layers_direct(n[0], 77.3598)

#for ii in range(0,41):
#    m = mirror.Mirror(wavelength=1083, n_subs=1.45)
#    print "=== {0} double layers ===".format(ii)
#    m.add_layers(n, d, repeat=ii)
#    m.add_layers(n[0], 0.25)
#    m.add_layers_direct(n[1], 270)
#    rs, rp = m.get_reflectivity()
#    print "\tR @ 1064nm: {:.4%}".format(rs)
#    rs, rp = m.get_reflectivity(1530)
#    print "\tR @ 1530nm: {:.4%}".format(rs)

rs, rp = m.get_reflectivity(1064)
print "\tR @ 1064nm: {:.4%}".format(rs)
rs, rp = m.get_reflectivity(1530)
print "\tR @ 1530nm: {:.4%}".format(rs)
print m.get_reflectivity(1038.5)[0]

print "num stacks: {:}, thickness: {:.3f}".format(len(m.stack.stacks_d), np.sum(m.stack.stacks_d))

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

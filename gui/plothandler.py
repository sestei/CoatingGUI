#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import os
from glob import glob
from importlib import import_module

def collect_plots():
    plots = {}
    for fn in glob('gui/plots/ui_*.ui'):
        mod = os.path.basename(os.path.splitext(fn)[0])
        mod = mod.replace('ui_plot', 'plot_')
        m = import_module('gui.plots.'+mod)
        plots.update(m.info)
    return plots

if __name__ == '__main__':
    print collect_plots()
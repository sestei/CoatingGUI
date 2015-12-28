#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import abc
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from dielectric.utils.config import Config
from gui.version import version_string

class BasePlotOptionWidget(QWidget):
    def __init__(self, name, parent):
        super(BasePlotOptionWidget, self).__init__(parent)
        ui_name = name if name.isupper() else name.title()
        uic.loadUi('gui/plots/ui_plot'+ui_name+'.ui', self)
        self.config = Config.Instance().view('plot.'+name)
        self.initialise_options()

    def initialise_options(self):
        pass

class BasePlot(object):
    """Base class for plots"""

    __metaclass__ = abc.ABCMeta

    # from http://www.huyng.com/posts/sane-color-scheme-for-matplotlib/
    colors = ['#348ABD',
              '#E24A33',
              '#988ED5',
              '#777777',
              '#FBC15E',
              '#8EBA42',
              '#FFB5B8']
    
    def __init__(self, name, handle):
        self.handle = handle
        self.handle.set_color_cycle(self.colors)
        self.config = Config.Instance().view('plot.'+name)

    @abc.abstractmethod
    def plot(self, coating):
        pass

    def add_grid(self, ax=None):
        if not ax:
            ax = self.handle
        ax.grid(which='major', color='0.7', linestyle='-')
        ax.grid(which='minor', color='0.7', linestyle=':')

    def add_legend(self, handles, entries):
        self.handle.legend(handles, entries, fontsize=10, frameon=False)

    def add_copyright(self):
        self.handle.set_title(version_string, loc='right', size=8)

#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import yaml
from utils import Singleton, version_number
from PyQt4.QtCore import QObject, pyqtSignal

@Singleton
class Config(QObject):
    modified = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self._config = {}
        self._modified = False
    
    def set(self, prop, value):
        _recursive_set(self._config, prop, value)
        if not self._modified:
            self._modified = True
            self.modified.emit()

    def get(self, prop):
        return _recursive_get(self._config, prop)

    def remove(self, prop):
        _recursive_remove(self._config, prop)
        if not self._modified:
            self._modified = True
            self.modified.emit()

    def load(self, filename):
        with file(filename, 'r') as fp:
            self._config = yaml.load(fp)
            self._modified = False
    
    def save(self, filename):
        with file(filename, 'w') as fp:
            self.set('version_number', version_number)
            yaml.dump(self._config, fp, default_flow_style=False)
            self._modified = False


def _recursive_set(thedict, key, value):
    try:
        idx = key.index('.')
        k = key[0:idx]
        if not k in thedict:
            thedict[k] = {}
        _recursive_set(thedict[k], key[idx+1:], value)
    except ValueError:
        thedict[key] = value

def _recursive_get(thedict, key):
    try:
        idx = key.index('.')
        k = key[0:idx]
        if not k in thedict:
            return None
        return _recursive_get(thedict[k], key[idx+1:])
    except ValueError:
        if key in thedict:
            return thedict[key]
        else:
            return None    

def _recursive_remove(thedict, key):
    try:
        idx = key.index('.')
        k = key[0:idx]
        if not k in thedict:
            return
        return _recursive_remove(thedict[k], key[idx+1:])
    except ValueError:
        if key in thedict:
            del(thedict[key])


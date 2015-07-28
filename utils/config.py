#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import yaml
import copy
from singleton import Singleton
from utils import version_number

class BasicConfig(object):
    _callback = None

    def __init__(self, filename=None):
        self._config = {}
        self._default = {}
        self._modified = False
        if filename:
            self.load(filename)
    
    def set_callback(self, callback):
        self._callback = callback

    def signal_callback(self):
        if self._callback:
            self._callback()

    def set(self, prop, value):
        _recursive_set(self._config, prop, value)
        if not self._modified:
            self._modified = True
            self.signal_callback()

    def get(self, prop):
        return _recursive_get(self._config, prop)

    def remove(self, prop):
        _recursive_remove(self._config, prop)
        if not self._modified:
            self._modified = True
            self.signal_callback()

    def view(self, path):
        return ConfigView(path)

    def load(self, filename):
        with file(filename, 'r') as fp:
            self._config = copy.deepcopy(self._default)
            self._config.update(yaml.load(fp))
            self._modified = False
    
    def load_default(self, filename):
        with file(filename, 'r') as fp:
            self._default = yaml.load(fp)
            self._config = copy.deepcopy(self._default)
            self._modified = False

    def save(self, filename):
        with file(filename, 'w') as fp:
            self.set('version_number', version_number)
            yaml.dump(self._config, fp, default_flow_style=False)
            self._modified = False

    @staticmethod
    def save_dict(thedict, filename):
        config = BasicConfig()
        config._config = thedict
        config.save(filename)


# Singleton version of the above BasicConfig object,
# useful for long-running applications
@Singleton
class Config(BasicConfig):
    pass


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


class ConfigView(object):
    """
    class ConfigView

    Represents a view onto a specific sub-tree of the
    configuration.
    """
    def __init__(self, base):
        if not base.endswith('.'):
            base = base + '.'
        self._base = base
        self._config = Config.Instance()

    def set(self, prop, value):
        self._config.set(self._base+prop, value)

    def get(self, prop):
        return self._config.get(self._base+prop)

    def remove(self, prop):
        self._config.remove(self._base+prop)

    @property
    def parent(self):
        return self._config

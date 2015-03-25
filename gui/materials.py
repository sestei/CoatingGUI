#!/usr/bin/env python

from utils import Singleton
from numpy import sqrt
from config import Config
from copy import copy

class MaterialAlreadyDefined(Exception):
    pass

class MaterialNotDefined(Exception):
    def __init__(self, material):
        self.material = material
    def __str__(self):
        return 'Undefined material {0}.'.format(self.material)

@Singleton
class MaterialLibrary(object):
    def __init__(self):
        self._materials = {}
        self.config = Config.Instance()

    def load_materials(self, matdict=None):
        if not matdict:
            # load all defined materials from config
            matdict = self.config.get('materials')
            # since we load directly from a fresh config, no need to unregister things
            self._materials = {}
        for name in matdict.iterkeys():
            self.create_material(self._unsanitize_name(name), matdict[name])

    def create_material(self, name, matdict):
        return Material(name=name, **matdict)

    def save_material(self, name):
        matdict = self._materials[name].save()
        self.config.set('materials.'+self._sanitize_name(name), matdict)

    def register(self, material):
        if not material.name in self._materials:
            self._materials[material.name] = material
        else:
            raise MaterialAlreadyDefined(material.name)

    def unregister(self, name):
        if name in self._materials:
            del(self._materials[name])
            self.config.remove('materials.'+self._sanitize_name(name))

    def list_materials(self):
        return self._materials.iterkeys()

    def get_material(self, material):
        try:
            n = float(material)
            return Material(n=n)
        except ValueError:
            try:
                return self._materials[material]
            except KeyError:
                raise MaterialNotDefined(material)

    def _sanitize_name(self, name):
        return name.replace('.', '~~')

    def _unsanitize_name(self, name):
        return name.replace('~~','.')


class Material(object):
    def __init__(self, name=None, n=0.0, B=None, C=None, notes=''):
        self.name = name
        self.notes = notes
        self.B = B if B else [0.0, 0.0, 0.0]
        self.C = C if C else [0.0, 0.0, 0.0]
        if n > 0.0:
            self.B[0] = n**2 - 1.0
            
        if self.name:
            MaterialLibrary.Instance().register(self)
        
    def n(self, lambda0):
        L = (lambda0 / 1000.0)**2; # Sellmeier equation works for um, not nm
        return sqrt(1+L*self.B[0]/(L-self.C[0])+L*self.B[1]/(L-self.C[1])+L*self.B[2]/(L-self.C[2]))

    def save(self):
        return {
            'B': self.B,
            'C': self.C,
            'notes': self.notes
        }


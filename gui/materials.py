#!/usr/bin/env python

from utils import Singleton
from numpy import sqrt
from config import Config
import abc

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
        mat = None
        if matdict['type'] == 'BaseMaterial':
            mat = BaseMaterial.restore(name, matdict)
        elif matdict['type'] == 'OpticalMaterial':
            mat = OpticalMaterial.restore(name, matdict)
        elif matdict['type'] == 'MechanicalMaterial':
            mat = MechanicalMaterial.restore(name, matdict)
        if not mat:
            print "Unknown material class encountered: {0}, ({1})".format(name, matdict['type'])

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
            return BaseMaterial(n=n)
        except ValueError:
            try:
                return self._materials[material]
            except KeyError:
                raise MaterialNotDefined(material)

    def _sanitize_name(self, name):
        return name.replace('.', '~~')

    def _unsanitize_name(self, name):
        return name.replace('~~','.')

class AbstractMaterial(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name=None,notes=''):
        self.name = name
        self.notes = notes
        if self.name:
            MaterialLibrary.Instance().register(self)
    
    @abc.abstractmethod
    def n(self, lambda0):
        """Returns the refractive index for wavelength lambda0"""
        pass

    def save(self):
        return {'type': 'AbstractMaterial', 'notes': self.notes}

    @staticmethod
    def restore(name, d):
        return None


class BaseMaterial(AbstractMaterial):
    """
    Implements a material with just a (constant) refractive index.
    Not suitable for thermal noise calculations.
    """
    def __init__(self, name=None, n=1.0, notes=''):
        super(BaseMaterial, self).__init__(name, notes)
        self._n = n
        
    def n(self, lambda0):
        return self._n

    def save(self):
        d = super(BaseMaterial, self).save()
        d['type'] = 'BaseMaterial'
        d['n'] = self._n
        return d

    @staticmethod
    def restore(name, d):
        return BaseMaterial(name,n=d['n'], notes=d['notes'])

class OpticalMaterial(AbstractMaterial):
    """
    Implements a material with wavelength-dependant
    refractive index, implemented via a Sellmeier equation.
    Not suitable for thermal noise calculations.
    """
    def __init__(self, name, B=[0.0, 0.0, 0.0], C=[0.0, 0.0, 0.0], notes=''):
        super(OpticalMaterial, self).__init__(name, notes)
        self.B = B
        self.C = C

    def n(self, lambda0):
        L = (lambda0 / 1000.0)**2; # Sellmeier equation works for um, not nm
        return sqrt(1+L*self.B[0]/(L-self.C[0])+L*self.B[1]/(L-self.C[1])+L*self.B[2]/(L-self.C[2]))

    def save(self):
        d = super(OpticalMaterial, self).save()
        d['type'] = 'OpticalMaterial'
        d['B'] = self.B
        d['C'] = self.C
        return d
        
    @staticmethod
    def restore(name, d):
        return OpticalMaterial(name, B=d['B'], C=d['C'],
            notes=d['notes'])


class MechanicalMaterial(OpticalMaterial):
    """
    Implements a material with wavelength-dependant
    refractive index, implemented via a Sellmeier equation,
    as well as mechanical and thermal properties.
    Suitable for thermal noise calculations.
    """
    pass


if __name__ == '__main__':
    air = BaseMaterial('Air', 1.0)
    fs = BaseMaterial('Fused Silica', 1.45)
    corning = OpticalMaterial('Corning 7980')
    # from corning.com datasheet
    corning.B = [0.68374049400,0.42032361300,0.58502748000]
    corning.C = [0.00460352869,0.01339688560,64.49327320000]

    for m in MaterialLibrary.Instance().list_materials():
        print m

    fs._n = 2.0
    print fs.n(1)
    print BaseMaterial.create('Fused Silica').n(1)
    print corning.n(1064)

    print globals['OpticalMaterial']

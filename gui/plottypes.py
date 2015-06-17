#!/usr/bin/env python
import numpy as np
import matplotlib
from config import Config


def add_copyright(plot):
    """Adds copyright notice to plot"""
    plot.set_title('CoatingGUI v0.1', loc='right', size=8)

def get_alpha(n):
    """Converts refractive index n into alpha transparency value"""
    return min(np.log(n)/1.39, 1.0)



#TODO: this whole thing should probably be split across several files,
#      maybe in a plugin-type approach
#TODO: put each plot in a subclass of some Plot superclass
#TODO: have the plot subclasses provide default x- and y-limits etc.

class PlotContainer(object):
    @classmethod
    def get_plottypes(cls):
        plottypes = []
        for kk in sorted(cls.__dict__.keys()):
            if kk.startswith('plot_'):
                func = getattr(cls, kk)
                plottypes.append((func.__doc__, func))
        return plottypes

    @staticmethod
    def plot_refractive_index(plot, coating):
        "Electric Field Intensity"

        stack = coating.create_stack(Config.Instance().get('coating.lambda0'))
        total_d = np.sum(stack.stacks_d)
        xmin = -0.2*total_d
        xmax = total_d - xmin
        xvalues = len(stack.stacks_d) * 2 + 4
        X = np.zeros(xvalues)
        Y = np.zeros(xvalues)
        X[0] = xmin; X[1] = -1; X[-1] = xmax; X[-2] = total_d
        Y[0] = Y[1] = stack.stacks_n[0]
        Y[-1] = Y[-2] = stack.stacks_n[-1]
        ii = 1
        current_d = 0
        for d, n in zip(stack.stacks_d, stack.stacks_n[1:-1]):
            X[ii*2] = current_d
            X[ii*2+1] = current_d+d-1
            Y[ii*2] = Y[ii*2+1] = n
            current_d += d
            ii += 1
        
        Xefi,Yefi = stack.efi(Config.Instance().get('coating.lambda0'))
        plot.plot(X,Y,Xefi,Yefi)

        for ii in range(0, xvalues/2):
            plot.axvspan(X[ii*2], X[ii*2+1], color=(0.52,0.61,0.73), alpha=get_alpha(Y[ii*2]))
            if ii == 0:
                text = 'superstrate'
            elif ii == xvalues/2 - 1:
                text = 'substrate'
            else:
                text = '{:.0f}nm'.format(stack.stacks_d[ii-1])
            plot.text((X[ii*2]+X[ii*2+1])/2, 0.8, text,
                      horizontalalignment='center', rotation='vertical')

        plot.set_xlim(xmin, xmax)
        plot.set_ylim(0, np.max(stack.stacks_n)+1)
        plot.set_ylabel('Refractive Index')
        plot.set_xlabel('Position (nm)')
        add_copyright(plot)

    @staticmethod
    def plot_reflectivity_wavelength(plot, coating):
        "Reflectivity vs. wavelength"

        def to_refl(val, position):
            refl = 1-10**(-val)
            return '{:.7g}'.format(refl)

        yLocator = matplotlib.ticker.MultipleLocator(1.0)
        yFormatter = matplotlib.ticker.FuncFormatter(to_refl)
        
        config = Config.Instance()
        #TODO: this assumes linear x axis, but log x axis maybe doesn't make much sense anyway
        #TODO: refactor this into another function, which can be used to plot transmission as well
        
        if config.get('plot.xaxis.limits') == 'auto':
            lambda0 = config.get('coating.lambda0')
            xlim = [0.7 * lambda0, 1.3 * lambda0]
        else:
            xlim = [config.get('plot.xaxis.min'), config.get('plot.xaxis.max')]
        
        X = np.linspace(*xlim, num=config.get('plot.xaxis.steps'))
        Y = np.zeros((len(X), 2))

        AOI = config.get('coating.AOI')
        for step in range(len(X)):
            stack = coating.create_stack(X[step], AOI=AOI)
            Y[step,:] = stack.reflectivity(X[step])

        auto_y = config.get('plot.yaxis.limits') == 'auto'
        
        ylim = [config.get('plot.yaxis.min'), config.get('plot.yaxis.max')]
        
        if config.get('plot.yaxis.scale') == 'log':
            Y = -np.log10(1.0-Y)
            if auto_y:
                ylim[0] = 0.3
                ylim[1] = np.ceil(np.max(Y))
            else:
                ylim[0] = -np.log10(1.0-ylim[0])
                ylim[1] = -np.log10(1.0-ylim[1]+1e-6)

        handles = plot.plot(X,Y)

        plot.grid(which='both')
        plot.set_xlim(xlim)
        plot.set_ylim(ylim)
        
        if config.get('plot.yaxis.scale') == "log":
            plot.set_yscale('log')
            plot.yaxis.set_major_formatter(yFormatter)
            plot.yaxis.set_major_locator(yLocator)

        plot.set_xlabel('Wavelength (nm)')
        plot.set_ylabel('Reflectivity')
        plot.legend(handles, ['s pol', 'p pol'])
        add_copyright(plot)

    @staticmethod
    def plot_reflectivity_aoi(plot, coating):
        "Reflectivity vs. AOI"

        config = Config.Instance()
        #TODO: this assumes linear x axis, but log x axis maybe doesn't make much sense anyway
        #TODO: we need an angle of incidence definable somewhere!
        if config.get('plot.xaxis.limits') == 'auto':
            xmin = 0.0
            xmax = max(60,config.get('coating.AOI'))
        else:
            xmin = config.get('plot.xaxis.min')
            xmax = config.get('plot.xaxis.max')

        X = np.linspace(xmin, xmax, config.get('plot.xaxis.steps'))
        Y = np.zeros((len(X), 2))

        lambda0 = config.get('coating.lambda0')
        for step in range(len(X)):
            stack = coating.create_stack(lambda0, AOI=X[step])
            Y[step,:] = stack.reflectivity(lambda0)

        handles = plot.plot(X,Y*100.0)
        
        plot.set_xlim(xmin, xmax)
        if config.get('plot.yaxis.limits') == 'auto':
            plot.set_ylim(0, 100.0)
        else:
            plot.set_ylim(config.get('plot.yaxis.min'), config.get('plot.yaxis.max'))

        if config.get('plot.yaxis.scale') == "log":
            plot.set_yscale('log')
        plot.grid(which='both')
        plot.set_xlabel('AOI (deg)')
        plot.set_ylabel('Reflectivity (%)')
        plot.legend(handles, ['s pol', 'p pol'])
        add_copyright(plot)

    @staticmethod
    def plot_phase_wavelength(plot, coating):
        "Phase vs. wavelength"

        config = Config.Instance()
        #TODO: this assumes linear x axis, but log x axis maybe doesn't make much sense anyway
        #TODO: we need an angle of incidence definable somewhere!
        #TODO: refactor this into another function, which can be used to plot transmission as well
        
        if config.get('plot.xaxis.limits') == 'auto':
            lambda0 = config.get('coating.lambda0')
            xmin = 0.7 * lambda0
            xmax = 1.3 * lambda0
        else:
            xmin = config.get('plot.xaxis.min')
            xmax = config.get('plot.xaxis.max')
        
        X = np.linspace(xmin, xmax, config.get('plot.xaxis.steps'))
        Y = np.zeros((len(X), 3))

        AOI = config.get('coating.AOI')
        for step in range(len(X)):
            stack = coating.create_stack(X[step], AOI=AOI)
            Y[step,:] = stack.phase(X[step])

        handles = plot.plot(X,(np.unwrap(Y, axis=0)%(2*np.pi))*180/np.pi)
        #handles = plot.plot(X,Y*180/np.pi)
        
        plot.set_xlim(xmin, xmax)
        if config.get('plot.yaxis.limits') == 'auto':
            #plot.set_ylim(-180, 180.0)
            pass
        else:
            plot.set_ylim(config.get('plot.yaxis.min'), config.get('plot.yaxis.max'))

        if config.get('plot.yaxis.scale') == "log":
            plot.set_yscale('log')
        plot.grid(which='major', color='0.7', linestyle='-')
        plot.grid(which='minor', color='0.7', linestyle=':')
        plot.minorticks_on()
        plot.set_xlabel('Wavelength (nm)')
        plot.set_ylabel('Phase (deg)')
        plot.legend(handles, ['s pol', 'p pol', 'delta'])
        add_copyright(plot)


# list all defined plot types here
plottypes = PlotContainer.get_plottypes()

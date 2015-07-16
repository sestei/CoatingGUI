import sys
import os
import glob
import shutil
from cx_Freeze import setup, Executable

def collect_plots():
    uis = []
    mods = []
    for fn in glob.glob('gui/plots/ui_*.ui'):
        uis.append(fn)
        mod = os.path.basename(os.path.splitext(fn)[0])
        mod = mod.replace('ui_plot', 'plot_')
        mods.append('gui.plots.'+mod)
    return (uis, mods)

def collect_uis():
    uis = []
    for fn in glob.glob('gui/ui_*.ui'):
        uis.append(fn)
    return uis

plot_uis, plot_mods = collect_plots()
uis = collect_uis()

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    packages = [],
    includes = ['gui.matplotlibwidget'] + plot_mods,
    excludes = ['scipy',
                'tcl',
                'tkinter'],
    include_files = ['default.cgp',
                     'gui/icons',
                     'gui/data',
                     ] + plot_uis + uis,
    build_exe = './dist/'
)

base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('CoatingGUI.py',
                base=base,
                targetName = 'coatinggui.exe',
                compress=True,
                targetDir='./dist/',
                icon='./gui/icons/coatinggui.ico')
]

setup(name='CoatingGUI',
      version = '0.2',
      description = 'CoatingGUI calculates dielectric mirror coatings.',
      options = dict(build_exe = buildOptions),
      executables = executables)

# Now clean up unnecessary stuff
if sys.platform == 'win32':
    remove_dirs = ['mpl-data/images', 'mpl-data/sample_data', 'PyQt4.uic.widget-plugins', 'tcl', 'tk']
    remove_files = ['numpy.core._dotblas.pyd', 'PyQt4.QtNetwork.pyd', 'PyQt4.QtWebKit.pyd',
                    'QtNetwork4.dll', 'QtWebKit4.dll', 'tcl85.dll', 'tk85.dll', 'wx._controls_.pyd',
                    'wx._core_.pyd', 'wx._gdi_.pyd', 'wx._misc_.pyd', 'wx._windows_.pyd',
                    'wxbase28uh_net_vc.dll', 'wxbase28uh_vc.dll', 'wxmsw28uh_adv_vc.dll',
                    'wxmsw28uh_core_vc.dll', 'wxmsw28uh_html_vc.dll']

    for dd in remove_dirs:
        path = './dist/'+dd
        print 'Cleaning up', path
        try:
            shutil.rmtree(path)
        except Exception, e:
            print e

    for ff in remove_files:
        path = './dist/'+ff
        print 'Cleaning up', path
        try:
            os.remove(path)
        except Exception, e:
            print e


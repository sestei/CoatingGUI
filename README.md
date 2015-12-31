CoatingGUI
==========

Dielectric mirror coating simulation tool

Status
------
- basic work flow implemented
- create arbitrary multi-layer coatings
- define optical materials based on refractive index, Sellmeier coefficients or
  measured data
- calculates reflectivity, EFI, room-temperature Brownian thermal noise

Screenshots
-----------

<img src="refl_vs_wavelength.png" />

Plot of reflectivity vs. wavelength for a multi-layer, quarter-wave stack HR
coating. The table on the left is used to enter the stack. Inputs like "l/4"
or just "/4" are automatically converted to the corresponding lambda/N
thickness for the given refractive index.

<img src="refr_index_profile.png" />

Plot of the refractive index profile and electric field intensity for the
above coating, for zero degrees angle of incidence.

<img src="material_editor.png" />

Thin-film and bulk materials can be defined in a graphical editor, here showing various possibilities to enter the refractive index: as a single value that is used across all wavelengths, as a Sellmeier equation, or as datapoints that are read in from a file.

Prerequisites
-------------

- Python >= 2.7
- PyQT 4
- numpy
- coatingtk (https://github.com/sestei/coatingtk)

---
-- Sebastian Steinlechner, 2015

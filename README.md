# xleaf

![docs/spectra.png](Canopy reflectance simulated in rainbows.)

<p align="center">
    <em>Leaf and canopy radiative transfer modeling tools built on PROSPECT-D and SAIL.</em>
</p>

---

## Introduction

🌳 `xleaf` is a python package for running leaf and canopy simulation models using PROSAIL. It provides python bindings to the PROSPECT-D & 4SAIL [Fortran code](http://teledetection.ipgp.jussieu.fr/prosail/).

🌿 It includes sensible defaults that make it easy to get up and running quickly, and clear code documentation in the form of docstrings and type hints.

---

## Usage

```python
import xleaf
import matplotlib.pyplot as plt

# run with off-the-shelf defaults
leaf = xleaf.simulate_leaf()

# or specify detailed parameters
canopy = xleaf.simulate_canopy(
    chl = 40, # ug/cm2
    car = 8, # ug/cm2
    antho = 0.5, # ug/cm2
    ewt = 0.01, # cm
    lma = 0.009, # g/cm2
    N = 1.5, # unitless
    lai = 3.0, # m2/m2
    lidf = 30, # degrees
    soil_dryness = 0.75, # %
    solar_zenith = 35, # degrees
    solar_azimuth = 120, # degrees
    view_zenith = 0, # degrees
    view_azimuth = 60, # degrees
    hot_spot = 0.01, # unitless
)

# and plot them together
plt.plot(xleaf.parameters.wavelengths, leaf, label='leaf')
plt.plot(xleaf.parameters.wavelengths, canopy, label='canopy')
plt.legend()
```

The definition and expected range of values for each parameter is described in the `xleaf` docstrings.

---

## Install

```
pip install xleaf
```

This may require a FORTRAN compiler. So on ubuntu could `sudo apt install gcc` and on macos you'd run `brew install gcc`.

---

## Developed by

[Christopher Anderson](https://cbanderson.info)[^1] [^2]

<a href="https://twitter.com/earth_chris">![Twitter Follow](https://img.shields.io/twitter/follow/earth_chris)</a>
<a href="https://github.com/earth-chris">![GitHub Stars](https://img.shields.io/github/stars/earth-chris?affiliations=OWNER%2CCOLLABORATOR&style=social)</a>

[^1]: [Planet Labs PBC, San Francisco](https://planet.com)
[^2]: [Center for Conservation Biology, Stanford University](https://ccb.stanford.edu)

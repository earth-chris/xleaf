"""Model parameters and methods for generating random parameter samples"""

import numpy as np

from xleaf.samplers import NormalSampler, UniformSampler

n_wavelengths = 2101
wavelengths = (np.arange(n_wavelengths) * 0.001) + 0.4
fwhms = np.ones(n_wavelengths, dtype=np.float32)
units = "micrometers"

LeafErectophile = (-1, 0)
LeafExtremophile = (0, 1)
LeafPlagiophile = (0, -1)
LeafPlanophile = (1, 0)
LeafSpherical = (-0.35, -0.15)
LeafUniform = (0, 0)

# solar/view azimuth: https://www.usgs.gov/landsat-missions/solar-illumination-and-sensor-viewing-angle-coefficient-files
# solar zenith: https://gis.stackexchange.com/questions/191692/maximum-solar-zenith-angle-for-landsat-8-images
AnthocyaninSampler = NormalSampler(mean=0.5, stdv=0.1, min=0.1, max=1)
ChlorophyllSampler = NormalSampler(mean=35, stdv=30, min=5, max=85)
CarotenoidSampler = NormalSampler(mean=8.75, stdv=7.5, min=2, max=15)
EWTSampler = NormalSampler(mean=0.03, stdv=0.01, min=0.005, max=0.05)
LAICropSampler = NormalSampler(mean=3.5, stdv=2.0, min=0.5, max=8.7)
LAIForestSampler = NormalSampler(mean=4.0, stdv=2.5, min=0.85, max=15)
LMASampler = NormalSampler(mean=0.012, stdv=0.005, min=0.005, max=0.025)
NSampler = NormalSampler(mean=2.2, stdv=0.3, min=1.25, max=3.6)
SoilDrynessSampler = UniformSampler(min=0.0, max=1.0)
SolarAzimuthSampler = UniformSampler(min=70.0, max=150.0)
SolarZenithSampler = UniformSampler(min=10.0, max=70.0)
ViewAzimuthSampler = UniformSampler(min=-150.0, max=150.0)
ViewZenithSampler = UniformSampler(min=0.0, max=10.0)

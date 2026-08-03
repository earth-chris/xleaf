import importlib.metadata

from xleaf import parameters, samplers
from xleaf.parameters import (
    AnthocyaninSampler,
    CarotenoidSampler,
    ChlorophyllSampler,
    EWTSampler,
    LAICropSampler,
    LAIForestSampler,
    LeafErectophile,
    LeafExtremophile,
    LeafPlagiophile,
    LeafPlanophile,
    LeafSpherical,
    LeafUniform,
    LMASampler,
    NormalSampler,
    NSampler,
    SoilDrynessSampler,
    SolarAzimuthSampler,
    SolarZenithSampler,
    UniformSampler,
    ViewAzimuthSampler,
    ViewZenithSampler,
    fwhms,
    wavelengths,
)
from xleaf.samplers import BaseSampler
from xleaf.simulators import simulate_canopy, simulate_leaf, simulate_sail

__version__ = importlib.metadata.version("xleaf")

__all__ = [
    "parameters",
    "samplers",
    "simulate_canopy",
    "simulate_leaf",
    "simulate_sail",
    "BaseSampler",
    "NormalSampler",
    "UniformSampler",
    "AnthocyaninSampler",
    "CarotenoidSampler",
    "ChlorophyllSampler",
    "EWTSampler",
    "LAICropSampler",
    "LAIForestSampler",
    "LMASampler",
    "NSampler",
    "SoilDrynessSampler",
    "SolarAzimuthSampler",
    "SolarZenithSampler",
    "ViewAzimuthSampler",
    "ViewZenithSampler",
    "LeafErectophile",
    "LeafExtremophile",
    "LeafPlagiophile",
    "LeafPlanophile",
    "LeafSpherical",
    "LeafUniform",
    "wavelengths",
    "fwhms",
]

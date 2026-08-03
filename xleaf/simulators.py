"""Methods for simulating leaf and canopy spectra."""

from typing import Tuple, Union

import numpy as np

from xleaf import prosail
from xleaf.parameters import LeafSpherical


def simulate_leaf(
    chl: float = 40,
    car: float = 8,
    antho: float = 0.5,
    ewt: float = 0.01,
    lma: float = 0.009,
    N: float = 1.5,
    transmittence: bool = False,
) -> np.ndarray:
    """Simulate a leaf reflectance profile based on structural/functional traits.

    Source: Feret, Gitelson, Noble & Jacqumoud (2017). PROSPECT-D: Towards modeling
        leaf optical properties through a complete lifecycle, RSE
        http://doi.org/10.1016/j.rse.2017.03.004

    Seee also: Rivera, Verrels, Leonenko & Moreno (2017)
        https://www.mdpi.com/2072-4292/5/7/3280

    Args:
        chl: chlorophyll a+b content (green pigments; ug/cm2).
            typical range is ~ 5 - 85.
        car: carotenoid content (orange/red pigments; ug/cm2).
            typically ~1/4 as abundant as chlorophyll a+b.
        antho: anthocyanin content (blue/purple pigments; ug/cm2).
            typically ~1/10 as abundant as carotenoids.
            but this is mostly anecdotal, not empirical.
        ewt: equivalent water thickness (cm)
            typical range is ~ 0.002 - 0.05.
        lma: leaf mass per unit area (g/cm2).
            typical range is ~ 0.002 - 0.036.
        N: leaf structure parameter (unitless)
            typical range is 1 - 3.6.
        transmittence: return transmittence spectra

    Returns:
        an array of shape (n_wavelengths,) if transmittence is false.
        of shape (2, n_wavelengths) with refl, trans as the row order.
    """
    # hardcode brown pigment value because no one but JB knows what it does
    # and even he sets it to 0
    cbrown = float(0)

    # cast all args to prevent bad fortran behavior
    chl = float(chl)
    car = float(car)
    antho = float(antho)
    ewt = float(ewt)
    lma = float(lma)
    N = float(N)

    # run the simulation
    refl, trans = prosail.prospect_db(N, chl, car, antho, cbrown, ewt, lma).transpose()

    if transmittence:
        return np.vstack((refl, trans))
    else:
        return refl


def simulate_canopy(
    chl: float = 40,
    car: float = 8,
    antho: float = 0.5,
    ewt: float = 0.01,
    lma: float = 0.009,
    N: float = 1.5,
    lai: float = 3.0,
    lidf: Union[float, Tuple[float, float]] = LeafSpherical,
    soil_dryness: float = 0.75,
    solar_zenith: float = 35,
    solar_azimuth: float = 120,
    view_zenith: float = 0,
    view_azimuth: float = 60,
    hot_spot: float = 0.01,
) -> np.ndarray:
    """Simulate a canopy reflectance profile based on structural/functional traits.

    Source: Feret, Gitelson, Noble & Jacqumoud (2017). PROSPECT-D: Towards modeling
        leaf optical properties through a complete lifecycle, RSE
        http://doi.org/10.1016/j.rse.2017.03.004

    See also: Rivera, Verrelst, Leonenko & Moreno (2017)
        https://www.mdpi.com/2072-4292/5/7/3280

    See also: Asner, Martin, Knapp, Tupayachi, Anderson, Carranza, Martinez,
        Houcheime, Sinca & Weiss (2011)
        http://dx.doi.org/10.1016/j.rse.2011.08.020

    Args:
        chl: chlorophyll a+b content (green pigments; ug/cm2).
            typical range is ~ 5 - 85.
        car: carotenoid content (orange/red pigment; ug/cm2).
            typically ~1/4 as abundant as chlorophyll a+b.
        antho: anthocyanin content (blue/purple pigments; ug/cm2).
            typically ~1/10 as abundant as carotenoids.
            but this is mostly anecdotal, not empirical.
        ewt: equivalent water thickness (cm)
            typical range is ~ 0.002 - 0.05.
        lma: leaf mass per unit area (g/cm2).
            typical range is ~ 0.002 - 0.036.
        N: leaf structure parameter (unitless)
            typical range is 1 - 3.6.
        lai: leaf area index (canopy leaf density; m2/m2)
            forest range is ~ 0.2 - 15
            crop range is ~ 0.2 - 8.7
        lidf: leaf inclination distribution function.
            can pass a single value for just the average leaf angle (degrees)
            or a tuple of (average leaf slope, bimodality), whose absolute
            values must sum to no more than 1. a near-spherical orientation
            would be (-0.35, -0.15).
            you can find some examples like `xleaf.parameters.LeafUniform`.
        soil_dryness: fraction of dry/wet soil. 1 indicates dry, 0 indicates wet.
        solar_zenith: solar zenith angle (degrees).
            range is a fairly uniform distribution from ~ 10 - 70.
        solar_azimuth: solar azimuth angle (degrees).
        view_zenith: sensor zenith angle (degrees).
            should be 0 for nadir-viewing instruments.
        view_azimuth: sensor azimuth angle (degrees).
        hot_spot: hot spot parameter (unitless).

    Returns:
        an array of shape (n_wavelengths,).
    """
    # hardcode brown pigment value to 0
    cbrown = float(0)

    # cast all args to prevent bad fortran behavior
    chl = float(chl)
    car = float(car)
    antho = float(antho)
    ewt = float(ewt)
    lma = float(lma)
    N = float(N)
    lai = float(lai)
    soil_dryness = float(soil_dryness)
    solar_zenith = np.abs(float(solar_zenith))
    solar_azimuth = float(solar_azimuth)
    view_zenith = np.abs(float(view_zenith))
    view_azimuth = float(view_azimuth)
    hot_spot = float(hot_spot)

    # compute relative azimuth angle in degrees (0..180) as expected by PROSAIL
    psi = float(np.abs((view_azimuth - solar_azimuth) % 360.0))
    psi = 360.0 - psi if psi > 180.0 else psi

    # handle multiple leaf type parameters
    try:
        leaf_slope, leaf_modality = float(lidf[0]), float(lidf[1])
        leaf_type = int(1)
    except TypeError:
        leaf_slope = float(lidf)
        leaf_modality = float(0)
        leaf_type = int(2)

    refl = prosail.simulate(
        N,
        chl,
        car,
        antho,
        cbrown,
        ewt,
        lma,
        soil_dryness,
        lai,
        hot_spot,
        solar_zenith,
        view_zenith,
        psi,
        leaf_type,
        leaf_slope,
        leaf_modality,
    )

    return refl


def simulate_sail(
    leaf_refl: np.ndarray,
    leaf_trans: np.ndarray,
    lai: float = 3.0,
    lidf: Union[float, Tuple[float, float]] = LeafSpherical,
    soil_dryness: float = 0.75,
    solar_zenith: float = 35,
    solar_azimuth: float = 120,
    view_zenith: float = 0,
    view_azimuth: float = 60,
    hot_spot: float = 0.01,
) -> np.ndarray:
    """Simulate a canopy reflectance profile from a supplied leaf spectrum.

    Runs only the 4SAIL canopy model, taking leaf optical properties as input
    instead of computing them with PROSPECT. Use this to run SAIL on a measured
    leaf spectrum, or one produced by another leaf model.

    Source: Verhoef, Jia, Xiao & Su (2007). Unified Optical-Thermal Four-Stream
        Radiative Transfer Theory for Homogeneous Vegetation Canopies, IEEE TGRS
        http://dx.doi.org/10.1109/TGRS.2007.895844

    Args:
        leaf_refl: leaf reflectance spectrum, shape (n_wavelengths,).
        leaf_trans: leaf transmittance spectrum, shape (n_wavelengths,).
            pair these with the output of `simulate_leaf(transmittence=True)`,
            which returns (refl, trans) as `spectrum[0]`, `spectrum[1]`.
        lai: leaf area index (canopy leaf density; m2/m2)
            forest range is ~ 0.2 - 15
            crop range is ~ 0.2 - 8.7
        lidf: leaf inclination distribution function.
            can pass a single value for just the average leaf angle (degrees)
            or a tuple of (average leaf slope, bimodality), whose absolute
            values must sum to no more than 1. a near-spherical orientation
            would be (-0.35, -0.15).
            you can find some examples like `xleaf.parameters.LeafUniform`.
        soil_dryness: fraction of dry/wet soil. 1 indicates dry, 0 indicates wet.
        solar_zenith: solar zenith angle (degrees).
            range is a fairly uniform distribution from ~ 10 - 70.
        solar_azimuth: solar azimuth angle (degrees).
        view_zenith: sensor zenith angle (degrees).
            should be 0 for nadir-viewing instruments.
        view_azimuth: sensor azimuth angle (degrees).
        hot_spot: hot spot parameter (unitless).

    Returns:
        an array of shape (n_wavelengths,).
    """
    # coerce leaf spectra to contiguous 1d float64 arrays for fortran
    leaf_refl = np.ascontiguousarray(leaf_refl, dtype=np.float64).ravel()
    leaf_trans = np.ascontiguousarray(leaf_trans, dtype=np.float64).ravel()

    # cast all args to prevent bad fortran behavior
    lai = float(lai)
    soil_dryness = float(soil_dryness)
    solar_zenith = np.abs(float(solar_zenith))
    solar_azimuth = float(solar_azimuth)
    view_zenith = np.abs(float(view_zenith))
    view_azimuth = float(view_azimuth)
    hot_spot = float(hot_spot)

    # compute relative azimuth angle in degrees (0..180) as expected by PROSAIL
    psi = float(np.abs((view_azimuth - solar_azimuth) % 360.0))
    psi = 360.0 - psi if psi > 180.0 else psi

    # handle multiple leaf type parameters
    try:
        leaf_slope, leaf_modality = float(lidf[0]), float(lidf[1])
        leaf_type = int(1)
    except TypeError:
        leaf_slope = float(lidf)
        leaf_modality = float(0)
        leaf_type = int(2)

    refl = prosail.simulate_sail(
        leaf_refl,
        leaf_trans,
        soil_dryness,
        lai,
        hot_spot,
        solar_zenith,
        view_zenith,
        psi,
        leaf_type,
        leaf_slope,
        leaf_modality,
    )

    return refl

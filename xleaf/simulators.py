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

    See also: Rivera, Verrels, Leonenko & Moreno (2017)
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
            or a tuple of (average leaf slope, bimodality), which together
            must sum to 1. a near-sperical orientation would be (-0.35, -0.15).
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
    solar_zenith = float(solar_zenith)
    solar_azimuth = float(solar_azimuth)
    view_zenith = float(view_zenith)
    view_azimuth = float(view_azimuth)
    hot_spot = float(hot_spot)

    # compute relative azmimuth angle
    psi = np.abs(view_azimuth - solar_azimuth)

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

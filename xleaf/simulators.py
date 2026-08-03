"""Methods for simulating leaf and canopy spectra."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from xleaf import prosail  # type: ignore[attr-defined]
from xleaf.parameters import LeafSpherical
from xleaf.validation import Lidf, as_spectrum, relative_azimuth, resolve_lidf

# brown pigment content, held at 0 as in the reference PROSAIL implementation
_CBROWN = 0.0


def simulate_leaf(
    chl: float = 40,
    car: float = 8,
    antho: float = 0.5,
    ewt: float = 0.01,
    lma: float = 0.009,
    N: float = 1.5,
    transmittance: bool = False,
) -> npt.NDArray[np.float64]:
    """Simulate a leaf reflectance profile based on structural/functional traits.

    Source: Feret, Gitelson, Noble & Jacquemoud (2017). PROSPECT-D: Towards modeling
        leaf optical properties through a complete lifecycle, RSE
        http://doi.org/10.1016/j.rse.2017.03.004

    See also: Rivera, Verrelst, Leonenko & Moreno (2017)
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
        transmittance: also return the transmittance spectrum.

    Returns:
        an array of shape (n_wavelengths,) with reflectance if transmittance is
        False, otherwise an array of shape (2, n_wavelengths) with reflectance
        and transmittance as the row order.

    Example:
        >>> import xleaf
        >>> refl = xleaf.simulate_leaf(chl=30)
        >>> refl, trans = xleaf.simulate_leaf(transmittance=True)
    """
    refl, trans = prosail.prospect_db(N, chl, car, antho, _CBROWN, ewt, lma).transpose()

    if transmittance:
        return np.vstack((refl, trans))
    return refl


def simulate_canopy(
    chl: float = 40,
    car: float = 8,
    antho: float = 0.5,
    ewt: float = 0.01,
    lma: float = 0.009,
    N: float = 1.5,
    lai: float = 3.0,
    lidf: Lidf = LeafSpherical,
    soil_dryness: float = 0.75,
    solar_zenith: float = 35,
    solar_azimuth: float = 120,
    view_zenith: float = 0,
    view_azimuth: float = 60,
    hot_spot: float = 0.01,
) -> npt.NDArray[np.float64]:
    """Simulate a canopy reflectance profile based on structural/functional traits.

    Runs PROSPECT-D and 4SAIL together: leaf optical properties are modeled from
    the leaf traits, then propagated through the canopy model.

    Source: Feret, Gitelson, Noble & Jacquemoud (2017). PROSPECT-D: Towards modeling
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

    Example:
        >>> import xleaf
        >>> canopy = xleaf.simulate_canopy(chl=40, lai=3.0, lidf=30)
    """
    psi = relative_azimuth(view_azimuth, solar_azimuth)
    leaf_type, leaf_slope, leaf_modality = resolve_lidf(lidf)

    return prosail.simulate(
        N,
        chl,
        car,
        antho,
        _CBROWN,
        ewt,
        lma,
        soil_dryness,
        lai,
        hot_spot,
        np.abs(solar_zenith),
        np.abs(view_zenith),
        psi,
        leaf_type,
        leaf_slope,
        leaf_modality,
    )


def simulate_sail(
    leaf_refl: npt.NDArray[np.float64],
    leaf_trans: npt.NDArray[np.float64],
    lai: float = 3.0,
    lidf: Lidf = LeafSpherical,
    soil_dryness: float = 0.75,
    solar_zenith: float = 35,
    solar_azimuth: float = 120,
    view_zenith: float = 0,
    view_azimuth: float = 60,
    hot_spot: float = 0.01,
) -> npt.NDArray[np.float64]:
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
            pair these with the output of `simulate_leaf(transmittance=True)`,
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

    Raises:
        ValueError: if either leaf spectrum is not length n_wavelengths.

    Example:
        >>> import xleaf
        >>> refl, trans = xleaf.simulate_leaf(transmittance=True)
        >>> canopy = xleaf.simulate_sail(refl, trans, lai=4, lidf=30)
    """
    leaf_refl = as_spectrum(leaf_refl)
    leaf_trans = as_spectrum(leaf_trans)

    psi = relative_azimuth(view_azimuth, solar_azimuth)
    leaf_type, leaf_slope, leaf_modality = resolve_lidf(lidf)

    return prosail.simulate_sail(
        leaf_refl,
        leaf_trans,
        soil_dryness,
        lai,
        hot_spot,
        np.abs(solar_zenith),
        np.abs(view_zenith),
        psi,
        leaf_type,
        leaf_slope,
        leaf_modality,
    )

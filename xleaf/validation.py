"""Input coercion and validation helpers shared across simulators."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from xleaf.parameters import n_wavelengths

Lidf = float | tuple[float, float]
"""Leaf inclination distribution: single average leaf angle (degrees), or a
(slope, bimodality) tuple."""


def resolve_lidf(lidf: Lidf) -> tuple[int, float, float]:
    """Resolve a leaf inclination distribution into PROSAIL parameters.

    Args:
        lidf: average leaf angle (degrees), or a (slope, bimodality) tuple.

    Returns:
        (leaf_type, slope, modality). leaf_type is 1 for the tuple form, 2 for
        the single-angle form.

    Raises:
        ValueError: if a sequence without exactly two items is passed.

    Example:
        >>> resolve_lidf(30)
        (2, 30.0, 0.0)
        >>> resolve_lidf((-0.35, -0.15))
        (1, -0.35, -0.15)
    """
    if isinstance(lidf, (tuple, list, np.ndarray)):
        if len(lidf) != 2:
            raise ValueError(f"a tuple lidf must have 2 items, got {len(lidf)}")
        return 1, float(lidf[0]), float(lidf[1])
    return 2, float(lidf), 0.0


def relative_azimuth(view_azimuth: float, solar_azimuth: float) -> float:
    """Relative azimuth angle folded into [0, 180] degrees.

    PROSAIL's volscatt compares the azimuth against transition angles in
    [0, pi], so the raw absolute difference (up to 360) must be folded.

    Args:
        view_azimuth: sensor azimuth angle (degrees).
        solar_azimuth: solar azimuth angle (degrees).

    Returns:
        relative azimuth in [0, 180] degrees.
    """
    psi = float(np.abs((view_azimuth - solar_azimuth) % 360.0))
    return 360.0 - psi if psi > 180.0 else psi


def as_spectrum(arr: npt.ArrayLike) -> npt.NDArray[np.float64]:
    """Coerce input to a contiguous 1d float64 spectrum of the expected length.

    Args:
        arr: array-like spectrum to coerce.

    Returns:
        contiguous 1d float64 array of length ``n_wavelengths``.

    Raises:
        ValueError: if the flattened length is not ``n_wavelengths``.
    """
    spectrum = np.ascontiguousarray(arr, dtype=np.float64).ravel()
    if spectrum.size != n_wavelengths:
        raise ValueError(f"spectrum must have length {n_wavelengths}, got {spectrum.size}")
    return spectrum

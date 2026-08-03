import numpy as np

import xleaf


def test_simulate_leaf():
    refl = xleaf.simulate_leaf(transmittence=False)
    rftl = xleaf.simulate_leaf(transmittence=True)
    assert not (refl == rftl).all()


def test_simulate_canopy():
    refl = xleaf.simulate_canopy()
    refl = xleaf.simulate_canopy(lidf=33)
    refl = xleaf.simulate_canopy(lidf=xleaf.parameters.LeafUniform)

    assert len(refl) == len(xleaf.parameters.wavelengths)


def test_simulate_sail():
    refl, trans = xleaf.simulate_leaf(transmittence=True)
    canopy = xleaf.simulate_sail(refl, trans)
    canopy = xleaf.simulate_sail(refl, trans, lidf=33)
    canopy = xleaf.simulate_sail(refl, trans, lidf=xleaf.parameters.LeafUniform)

    assert len(canopy) == len(xleaf.parameters.wavelengths)


def test_simulate_sail_matches_canopy():
    # SAIL on a PROSPECT leaf must reproduce the combined PROSPECT+SAIL path
    traits = dict(chl=40, car=8, antho=0.5, ewt=0.01, lma=0.009, N=1.5)
    canopy_kwargs = dict(
        lai=3.0,
        lidf=xleaf.parameters.LeafSpherical,
        soil_dryness=0.75,
        solar_zenith=35,
        solar_azimuth=120,
        view_zenith=0,
        view_azimuth=60,
        hot_spot=0.01,
    )

    refl, trans = xleaf.simulate_leaf(transmittence=True, **traits)
    from_sail = xleaf.simulate_sail(refl, trans, **canopy_kwargs)
    from_canopy = xleaf.simulate_canopy(**traits, **canopy_kwargs)

    np.testing.assert_allclose(from_sail, from_canopy, rtol=1e-10, atol=1e-12)


def test_simulate_sail_lai_zero():
    refl, trans = xleaf.simulate_leaf(transmittence=True)
    from_sail = xleaf.simulate_sail(refl, trans, lai=0)
    from_canopy = xleaf.simulate_canopy(lai=0)

    np.testing.assert_allclose(from_sail, from_canopy, rtol=1e-10, atol=1e-12)


def test_relative_azimuth_normalization():
    # psi must fold into [0, 180]: wrap-around and sign are symmetric
    wrapped = xleaf.simulate_canopy(solar_azimuth=350, view_azimuth=10)  # rel 340 -> 20
    flipped = xleaf.simulate_canopy(solar_azimuth=10, view_azimuth=350)  # rel 340 -> 20
    direct = xleaf.simulate_canopy(solar_azimuth=0, view_azimuth=20)  # rel 20

    np.testing.assert_allclose(wrapped, flipped, rtol=1e-12, atol=0)
    np.testing.assert_allclose(wrapped, direct, rtol=1e-12, atol=0)


def test_simulate_sail_azimuth_normalization():
    refl, trans = xleaf.simulate_leaf(transmittence=True)
    wrapped = xleaf.simulate_sail(refl, trans, solar_azimuth=350, view_azimuth=10)
    direct = xleaf.simulate_sail(refl, trans, solar_azimuth=0, view_azimuth=20)

    np.testing.assert_allclose(wrapped, direct, rtol=1e-12, atol=0)


def test_UniformSampler():
    min = 3
    max = 6
    us = xleaf.samplers.UniformSampler(min=min, max=max, seed=None)
    for _ in range(100):
        sample = us.sample()
        assert sample >= min
        assert sample <= max


def test_NormalSampler():
    mean = 5
    stdv = 4
    min = 0.3
    max = 12
    ns = xleaf.samplers.NormalSampler(mean=mean, stdv=stdv, min=min, max=max, seed=None)
    for _ in range(100):
        sample = ns.sample()
        assert sample >= min
        assert sample <= max

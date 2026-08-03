import numpy as np
import pytest

import xleaf
from xleaf import parameters
from xleaf.validation import as_spectrum, relative_azimuth, resolve_lidf

N_WL = parameters.n_wavelengths


class TestSimulateLeaf:
    def test_reflectance_shape(self):
        refl = xleaf.simulate_leaf(transmittance=False)
        assert refl.shape == (N_WL,)

    def test_transmittance_shape(self):
        both = xleaf.simulate_leaf(transmittance=True)
        assert both.shape == (2, N_WL)

    def test_reflectance_matches_transmittance_row(self):
        refl = xleaf.simulate_leaf()
        both = xleaf.simulate_leaf(transmittance=True)
        np.testing.assert_array_equal(refl, both[0])

    def test_reflectance_in_unit_range(self):
        refl = xleaf.simulate_leaf()
        assert np.all(refl >= 0) and np.all(refl <= 1)


class TestSimulateCanopy:
    def test_default_shape(self):
        assert xleaf.simulate_canopy().shape == (N_WL,)

    def test_scalar_and_tuple_lidf_differ(self):
        scalar = xleaf.simulate_canopy(lidf=33)
        tup = xleaf.simulate_canopy(lidf=parameters.LeafUniform)
        assert not np.allclose(scalar, tup)

    def test_lai_zero_is_soil(self):
        # with no leaves the canopy reflects the soil only; two leaf sets agree
        a = xleaf.simulate_canopy(lai=0, chl=20)
        b = xleaf.simulate_canopy(lai=0, chl=80)
        np.testing.assert_allclose(a, b, rtol=1e-12, atol=0)

    def test_bad_lidf_raises(self):
        with pytest.raises(ValueError, match="2 items"):
            xleaf.simulate_canopy(lidf=(1, 2, 3))


class TestSimulateSail:
    def leaf(self, **traits):
        return xleaf.simulate_leaf(transmittance=True, **traits)

    def test_default_shape(self):
        refl, trans = self.leaf()
        assert xleaf.simulate_sail(refl, trans).shape == (N_WL,)

    def test_scalar_and_tuple_lidf_differ(self):
        refl, trans = self.leaf()
        scalar = xleaf.simulate_sail(refl, trans, lidf=33)
        tup = xleaf.simulate_sail(refl, trans, lidf=parameters.LeafUniform)
        assert not np.allclose(scalar, tup)

    def test_matches_canopy(self):
        traits = dict(chl=40, car=8, antho=0.5, ewt=0.01, lma=0.009, N=1.5)
        canopy_kwargs = dict(
            lai=3.0,
            lidf=parameters.LeafSpherical,
            soil_dryness=0.75,
            solar_zenith=35,
            solar_azimuth=120,
            view_zenith=0,
            view_azimuth=60,
            hot_spot=0.01,
        )
        refl, trans = self.leaf(**traits)
        from_sail = xleaf.simulate_sail(refl, trans, **canopy_kwargs)
        from_canopy = xleaf.simulate_canopy(**traits, **canopy_kwargs)
        np.testing.assert_allclose(from_sail, from_canopy, rtol=1e-10, atol=1e-12)

    def test_lai_zero_matches_canopy(self):
        refl, trans = self.leaf()
        np.testing.assert_allclose(
            xleaf.simulate_sail(refl, trans, lai=0),
            xleaf.simulate_canopy(lai=0),
            rtol=1e-10,
            atol=1e-12,
        )

    def test_accepts_2d_spectrum_rows(self):
        both = self.leaf()
        canopy = xleaf.simulate_sail(both[0], both[1])
        assert canopy.shape == (N_WL,)

    def test_wrong_length_spectrum_raises(self):
        refl, trans = self.leaf()
        with pytest.raises(ValueError, match="spectrum must have length"):
            xleaf.simulate_sail(refl[:-1], trans)


class TestAzimuthNormalization:
    def test_canopy_wrap_and_flip_symmetry(self):
        wrapped = xleaf.simulate_canopy(solar_azimuth=350, view_azimuth=10)
        flipped = xleaf.simulate_canopy(solar_azimuth=10, view_azimuth=350)
        direct = xleaf.simulate_canopy(solar_azimuth=0, view_azimuth=20)
        np.testing.assert_allclose(wrapped, flipped, rtol=1e-12, atol=0)
        np.testing.assert_allclose(wrapped, direct, rtol=1e-12, atol=0)

    def test_sail_wrap_matches_direct(self):
        refl, trans = xleaf.simulate_leaf(transmittance=True)
        wrapped = xleaf.simulate_sail(refl, trans, solar_azimuth=350, view_azimuth=10)
        direct = xleaf.simulate_sail(refl, trans, solar_azimuth=0, view_azimuth=20)
        np.testing.assert_allclose(wrapped, direct, rtol=1e-12, atol=0)


class TestValidationHelpers:
    def test_resolve_lidf_scalar(self):
        assert resolve_lidf(30) == (2, 30.0, 0.0)

    def test_resolve_lidf_tuple(self):
        assert resolve_lidf((-0.35, -0.15)) == (1, -0.35, -0.15)

    def test_resolve_lidf_bad_length_raises(self):
        with pytest.raises(ValueError, match="2 items"):
            resolve_lidf((1, 2, 3))

    @pytest.mark.parametrize(
        "view,solar,expected",
        [(60, 120, 60.0), (10, 350, 20.0), (350, 10, 20.0), (200, 0, 160.0)],
    )
    def test_relative_azimuth_folds_into_range(self, view, solar, expected):
        assert relative_azimuth(view, solar) == pytest.approx(expected)

    def test_as_spectrum_flattens_2d_row(self):
        arr = np.zeros((1, N_WL))
        assert as_spectrum(arr).shape == (N_WL,)

    def test_as_spectrum_wrong_length_raises(self):
        with pytest.raises(ValueError, match="must have length"):
            as_spectrum(np.zeros(10))


class TestUniformSampler:
    def test_bounds(self):
        us = xleaf.UniformSampler(min=3, max=6, seed=None)
        samples = [us.sample() for _ in range(100)]
        assert all(3 <= s <= 6 for s in samples)

    def test_seed_reproducible(self):
        a = xleaf.UniformSampler(min=0, max=1, seed=42)
        b = xleaf.UniformSampler(min=0, max=1, seed=42)
        assert a.sample() == b.sample()


class TestNormalSampler:
    def test_bounds(self):
        ns = xleaf.NormalSampler(mean=5, stdv=4, min=0.3, max=12, seed=None)
        samples = [ns.sample() for _ in range(100)]
        assert all(0.3 <= s <= 12 for s in samples)

    def test_seed_reproducible(self):
        a = xleaf.NormalSampler(mean=0, stdv=1, seed=42)
        b = xleaf.NormalSampler(mean=0, stdv=1, seed=42)
        assert a.sample() == b.sample()

    def test_one_sided_bound_does_not_crash(self):
        # only min set: the rejection loop must not compare against a None max
        ns = xleaf.NormalSampler(mean=5, stdv=2, min=0, seed=1)
        assert isinstance(ns.sample(), float)

    def test_unbounded_returns_float(self):
        ns = xleaf.NormalSampler(mean=0, stdv=1, seed=1)
        assert isinstance(ns.sample(), float)


class TestBaseSampler:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            xleaf.BaseSampler()


class TestParameters:
    def test_wavelengths_length(self):
        assert len(parameters.wavelengths) == N_WL

    def test_wavelengths_range(self):
        assert parameters.wavelengths[0] == pytest.approx(0.4)
        assert parameters.wavelengths[-1] == pytest.approx(2.5)

    def test_fwhms_shape_and_dtype(self):
        assert parameters.fwhms.shape == (N_WL,)
        assert parameters.fwhms.dtype == np.float32

    def test_lidf_presets_exported(self):
        for name in (
            "LeafErectophile",
            "LeafExtremophile",
            "LeafPlagiophile",
            "LeafPlanophile",
            "LeafSpherical",
            "LeafUniform",
        ):
            assert hasattr(xleaf, name)

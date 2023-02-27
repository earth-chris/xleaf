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

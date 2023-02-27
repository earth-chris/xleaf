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

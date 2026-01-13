import numpy as np
import pytest
from shield_lite.optimization.calibration import fit_S, fit_S_mu_eff

def test_fit_S():
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = fit_S(y)
    assert 'S' in result
    assert isinstance(result['S'], float)

def test_fit_S_mu_eff():
    t = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = fit_S_mu_eff(t, y)
    assert 'mu_eff' in result
    assert isinstance(result['mu_eff'], float)
    assert 'S' in result
    assert isinstance(result['S'], float)
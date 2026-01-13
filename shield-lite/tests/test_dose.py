import pytest
from shield_lite.core.dose import dose

def test_dose():
    thicknesses = {'lead': 10.0, 'concrete': 20.0}
    mu = {'lead': 0.1, 'concrete': 0.05}
    S = 100.0
    expected_dose = S * (1 - (1 - mu['lead']) ** thicknesses['lead']) * (1 - (1 - mu['concrete']) ** thicknesses['concrete'])
    
    calculated_dose = dose(thicknesses, mu, S)
    
    assert abs(calculated_dose - expected_dose) < 1e-6

def test_dose_zero_thickness():
    thicknesses = {'lead': 0.0, 'concrete': 0.0}
    mu = {'lead': 0.1, 'concrete': 0.05}
    S = 100.0
    expected_dose = 0.0
    
    calculated_dose = dose(thicknesses, mu, S)
    
    assert calculated_dose == expected_dose

def test_dose_negative_thickness():
    thicknesses = {'lead': -5.0, 'concrete': 10.0}
    mu = {'lead': 0.1, 'concrete': 0.05}
    S = 100.0
    
    with pytest.raises(ValueError):
        dose(thicknesses, mu, S)
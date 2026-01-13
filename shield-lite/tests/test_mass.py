import pytest
from shield_lite.core.mass import mass

def test_mass_calculation():
    thicknesses = {'lead': 10.0, 'iron': 5.0}
    densities = {'lead': 11.34, 'iron': 7.87}  # g/cm^3
    area_m2 = 1.0  # m^2

    expected_mass = (thicknesses['lead'] * densities['lead'] + 
                     thicknesses['iron'] * densities['iron']) * 1000  # Convert to kg

    calculated_mass = mass(thicknesses, densities, area_m2)
    
    assert abs(calculated_mass - expected_mass) < 1e-6  # Allow for small floating point errors

def test_mass_with_zero_area():
    thicknesses = {'lead': 10.0}
    densities = {'lead': 11.34}  # g/cm^3
    area_m2 = 0.0  # m^2

    calculated_mass = mass(thicknesses, densities, area_m2)
    
    assert calculated_mass == 0.0  # Mass should be zero if area is zero

def test_mass_with_empty_thicknesses():
    thicknesses = {}
    densities = {}
    area_m2 = 1.0  # m^2

    calculated_mass = mass(thicknesses, densities, area_m2)
    
    assert calculated_mass == 0.0  # Mass should be zero if no materials are provided
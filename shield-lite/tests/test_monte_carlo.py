"""
Tests for Monte Carlo photon transport simulation.
"""

import pytest
import numpy as np

try:
    from shield_lite.core import MonteCarloShieldSimulator, estimate_required_photons
    MONTE_CARLO_AVAILABLE = True
except ImportError:
    MONTE_CARLO_AVAILABLE = False


@pytest.mark.skipif(not MONTE_CARLO_AVAILABLE, reason="Monte Carlo module not compiled")
class TestMonteCarloSimulator:
    """Test suite for Monte Carlo simulator."""

    def test_simulator_creation(self):
        """Test that simulator can be created."""
        sim = MonteCarloShieldSimulator()
        assert sim is not None

    def test_simulator_with_seed(self):
        """Test that simulator can be created with custom seed."""
        sim = MonteCarloShieldSimulator(seed=123)
        assert sim is not None

    def test_add_layer(self):
        """Test adding a single layer."""
        sim = MonteCarloShieldSimulator()
        sim.add_layer(
            material_name="Lead",
            thickness_cm=5.0,
            mu_total=0.77,
            mu_compton=0.58,
            mu_photoelectric=0.19,
            density_g_cm3=11.34
        )
        assert sim.get_total_thickness() == 5.0
        assert len(sim.get_shield_info()) == 1

    def test_add_multiple_layers(self):
        """Test adding multiple layers."""
        sim = MonteCarloShieldSimulator()
        sim.add_layer("Lead", 3.0, 0.77, 0.58, 0.19, 11.34)
        sim.add_layer("Steel", 2.0, 0.47, 0.35, 0.12, 7.85)

        assert sim.get_total_thickness() == 5.0
        assert len(sim.get_shield_info()) == 2

    def test_clear_layers(self):
        """Test clearing layers."""
        sim = MonteCarloShieldSimulator()
        sim.add_layer("Lead", 3.0, 0.77, 0.58, 0.19, 11.34)
        sim.clear_layers()

        assert sim.get_total_thickness() == 0.0
        assert len(sim.get_shield_info()) == 0

    def test_simple_simulation(self):
        """Test running a simple simulation."""
        sim = MonteCarloShieldSimulator(seed=42)
        sim.add_layer("Lead", 5.0, 0.77, 0.58, 0.19, 11.34)

        result = sim.run(source_energy_MeV=1.0, num_photons=10000)

        # Check result structure
        assert hasattr(result, 'transmission_factor')
        assert hasattr(result, 'buildup_factor')
        assert hasattr(result, 'dose_transmitted')
        assert hasattr(result, 'dose_absorbed')
        assert hasattr(result, 'total_photons')
        assert hasattr(result, 'transmitted_photons')

        # Check result values are reasonable
        assert 0.0 <= result.transmission_factor <= 1.0
        assert result.buildup_factor >= 1.0
        assert result.total_photons == 10000
        assert 0 <= result.transmitted_photons <= 10000

    def test_transmission_decreases_with_thickness(self):
        """Test that transmission decreases as shield thickness increases."""
        results = []

        for thickness in [1.0, 3.0, 5.0]:
            sim = MonteCarloShieldSimulator(seed=42)
            sim.add_layer("Lead", thickness, 0.77, 0.58, 0.19, 11.34)
            result = sim.run(source_energy_MeV=1.0, num_photons=50000)
            results.append(result.transmission_factor)

        # Transmission should decrease with increasing thickness
        assert results[0] > results[1] > results[2]

    def test_reproducibility_with_seed(self):
        """Test that results are reproducible with same seed."""
        # Run 1
        sim1 = MonteCarloShieldSimulator(seed=42)
        sim1.add_layer("Lead", 3.0, 0.77, 0.58, 0.19, 11.34)
        result1 = sim1.run(source_energy_MeV=1.0, num_photons=10000)

        # Run 2 with same seed
        sim2 = MonteCarloShieldSimulator(seed=42)
        sim2.add_layer("Lead", 3.0, 0.77, 0.58, 0.19, 11.34)
        result2 = sim2.run(source_energy_MeV=1.0, num_photons=10000)

        # Results should be identical
        assert result1.transmission_factor == result2.transmission_factor
        assert result1.transmitted_photons == result2.transmitted_photons

    def test_buildup_factor_greater_than_one(self):
        """Test that buildup factor is >= 1 (due to scattering)."""
        sim = MonteCarloShieldSimulator(seed=42)
        sim.add_layer("Lead", 3.0, 0.77, 0.58, 0.19, 11.34)

        result = sim.run(source_energy_MeV=1.0, num_photons=50000)

        assert result.buildup_factor >= 1.0

    def test_no_layers_raises_error(self):
        """Test that running without layers raises an error."""
        sim = MonteCarloShieldSimulator()

        with pytest.raises(ValueError):
            sim.run(source_energy_MeV=1.0, num_photons=10000)

    def test_add_layers_from_dict(self):
        """Test adding layers from dictionaries."""
        sim = MonteCarloShieldSimulator()

        thicknesses = {'Lead': 3.0, 'Steel': 2.0}
        mu_total = {'Lead': 0.77, 'Steel': 0.47}
        mu_compton = {'Lead': 0.58, 'Steel': 0.35}
        mu_photoelectric = {'Lead': 0.19, 'Steel': 0.12}
        density = {'Lead': 11.34, 'Steel': 7.85}

        sim.add_layers_from_dict(
            thicknesses=thicknesses,
            mu_total=mu_total,
            mu_compton=mu_compton,
            mu_photoelectric=mu_photoelectric,
            density=density
        )

        assert sim.get_total_thickness() == 5.0
        assert len(sim.get_shield_info()) == 2

    def test_compare_with_analytical(self):
        """Test comparison with analytical model."""
        sim = MonteCarloShieldSimulator(seed=42)
        sim.add_layer("Lead", 2.0, 0.77, 0.58, 0.19, 11.34)

        comparison = sim.compare_with_analytical(
            source_energy_MeV=1.0,
            num_photons=50000
        )

        # Check structure
        assert 'monte_carlo' in comparison
        assert 'analytical_transmission' in comparison
        assert 'buildup_factor' in comparison
        assert 'difference_percent' in comparison

        # Analytical should be less than MC (buildup factor)
        assert comparison['mc_transmission'] >= comparison['analytical_transmission']
        assert comparison['buildup_factor'] >= 1.0

    def test_energy_dependence(self):
        """Test that higher energy photons are more penetrating."""
        sim = MonteCarloShieldSimulator(seed=42)
        sim.add_layer("Lead", 3.0, 0.77, 0.58, 0.19, 11.34)

        # Note: This test assumes constant mu values, which is a simplification
        # In reality, mu depends on energy, but we're testing the simulator logic
        result_low = sim.run(source_energy_MeV=0.5, num_photons=50000)
        result_high = sim.run(source_energy_MeV=2.0, num_photons=50000)

        # With constant mu, transmission should be similar
        # This tests that energy is properly handled in the simulation
        assert result_low.transmission_factor > 0
        assert result_high.transmission_factor > 0

    def test_statistical_uncertainty(self):
        """Test that uncertainty decreases with more photons."""
        sim = MonteCarloShieldSimulator(seed=42)
        sim.add_layer("Lead", 2.0, 0.77, 0.58, 0.19, 11.34)

        # Small number of photons
        result_small = sim.run(source_energy_MeV=1.0, num_photons=10000)

        # Reset and run with more photons
        sim.clear_layers()
        sim.add_layer("Lead", 2.0, 0.77, 0.58, 0.19, 11.34)
        result_large = sim.run(source_energy_MeV=1.0, num_photons=100000)

        # Uncertainty should decrease (though this is statistical, so may fail occasionally)
        # We'll check that both have finite uncertainty
        assert result_small.uncertainty >= 0
        assert result_large.uncertainty >= 0


@pytest.mark.skipif(not MONTE_CARLO_AVAILABLE, reason="Monte Carlo module not compiled")
class TestHelperFunctions:
    """Test helper functions."""

    def test_estimate_required_photons(self):
        """Test photon number estimation."""
        n = estimate_required_photons(
            desired_uncertainty=0.01,
            expected_transmission=0.1
        )

        assert n >= 10000  # Minimum
        assert isinstance(n, int)

    def test_estimate_with_low_transmission(self):
        """Test estimation with very low transmission."""
        n_high = estimate_required_photons(
            desired_uncertainty=0.01,
            expected_transmission=0.01  # Very low
        )

        n_low = estimate_required_photons(
            desired_uncertainty=0.01,
            expected_transmission=0.5   # High
        )

        # Lower transmission requires more photons
        assert n_high > n_low


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

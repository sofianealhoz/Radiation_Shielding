"""
Example: Monte Carlo simulation of gamma ray shielding

This example demonstrates how to use the Monte Carlo photon transport
simulation to calculate realistic dose transmission through a multi-layer shield.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from shield_lite.core import MonteCarloShieldSimulator, estimate_required_photons
    from shield_lite.core import dose as analytical_dose
except ImportError as e:
    print(f"Error: {e}")
    print("\nMake sure to compile the C++ extension first:")
    print("  cd shield-lite")
    print("  mkdir -p build && cd build")
    print("  cmake ..")
    print("  make")
    print("  cd ..")
    sys.exit(1)


def example_simple_lead_shield():
    """Example 1: Simple lead shield simulation."""
    print("=" * 70)
    print("Example 1: Single-layer Lead Shield")
    print("=" * 70)

    # Create simulator
    sim = MonteCarloShieldSimulator(seed=42)

    # Add 5 cm of lead
    # Typical values for 1 MeV gamma rays in lead:
    sim.add_layer(
        material_name="Lead",
        thickness_cm=5.0,
        mu_total=0.77,          # cm^-1 (total attenuation)
        mu_compton=0.58,        # cm^-1 (Compton scattering)
        mu_photoelectric=0.19,  # cm^-1 (photoelectric absorption)
        density_g_cm3=11.34     # g/cm^3
    )

    # Estimate required photons for 1% uncertainty
    expected_transmission = 0.02  # Rough estimate
    n_photons = estimate_required_photons(
        desired_uncertainty=0.01,
        expected_transmission=expected_transmission
    )
    print(f"\nEstimated photons needed: {n_photons:,}")

    # Run simulation
    print(f"\nRunning Monte Carlo with {n_photons:,} photons...")
    result = sim.run(source_energy_MeV=1.0, num_photons=n_photons)

    # Display results
    print(f"\nResults:")
    print(f"  Transmission factor:    {result.transmission_factor:.6f}")
    print(f"  Transmitted photons:    {result.transmitted_photons:,} / {result.total_photons:,}")
    print(f"  Buildup factor:         {result.buildup_factor:.3f}")
    print(f"  Avg dose transmitted:   {result.dose_transmitted:.6f} MeV/photon")
    print(f"  Avg dose absorbed:      {result.dose_absorbed:.6f} MeV/photon")
    print(f"  Statistical uncertainty: {result.uncertainty:.6f}")

    # Compare with analytical
    print(f"\nComparison with analytical (Beer-Lambert law):")
    comparison = sim.compare_with_analytical(
        source_energy_MeV=1.0,
        num_photons=n_photons
    )
    print(f"  Analytical transmission: {comparison['analytical_transmission']:.6f}")
    print(f"  Monte Carlo transmission: {comparison['mc_transmission']:.6f}")
    print(f"  Difference: {comparison['difference_percent']:.2f}%")
    print(f"  Buildup factor: {comparison['buildup_factor']:.3f}")

    print("\nInterpretation:")
    print(f"  The buildup factor of {result.buildup_factor:.2f} means that the actual dose")
    print(f"  is {result.buildup_factor:.2f}x higher than predicted by simple exponential")
    print(f"  attenuation, due to scattered photons reaching the detector.")


def example_multilayer_shield():
    """Example 2: Multi-layer shield with different materials."""
    print("\n" + "=" * 70)
    print("Example 2: Multi-layer Shield (Lead + Concrete + Steel)")
    print("=" * 70)

    # Create simulator
    sim = MonteCarloShieldSimulator(seed=123)

    # Add multiple layers (source -> detector)
    # Layer 1: Lead (inner layer, near source)
    sim.add_layer(
        material_name="Lead",
        thickness_cm=3.0,
        mu_total=0.77,
        mu_compton=0.58,
        mu_photoelectric=0.19,
        density_g_cm3=11.34
    )

    # Layer 2: Concrete (middle layer)
    sim.add_layer(
        material_name="Concrete",
        thickness_cm=10.0,
        mu_total=0.16,
        mu_compton=0.12,
        mu_photoelectric=0.04,
        density_g_cm3=2.3
    )

    # Layer 3: Steel (outer layer)
    sim.add_layer(
        material_name="Steel",
        thickness_cm=2.0,
        mu_total=0.47,
        mu_compton=0.35,
        mu_photoelectric=0.12,
        density_g_cm3=7.85
    )

    # Print shield info
    print("\nShield configuration:")
    for i, layer in enumerate(sim.get_shield_info(), 1):
        print(f"  Layer {i}: {layer['material']:10s} - {layer['thickness_cm']:.1f} cm")
    print(f"\nTotal thickness: {sim.get_total_thickness():.1f} cm")

    # Run simulation
    n_photons = 500_000
    print(f"\nRunning Monte Carlo with {n_photons:,} photons...")
    result = sim.run(source_energy_MeV=1.0, num_photons=n_photons)

    # Display results
    print(f"\nResults:")
    print(f"  Transmission factor:    {result.transmission_factor:.6f}")
    print(f"  Transmitted photons:    {result.transmitted_photons:,} / {result.total_photons:,}")
    print(f"  Buildup factor:         {result.buildup_factor:.3f}")
    print(f"  Statistical uncertainty: {result.uncertainty:.6f}")

    # Compare with analytical
    comparison = sim.compare_with_analytical(
        source_energy_MeV=1.0,
        num_photons=n_photons
    )
    print(f"\nComparison with analytical:")
    print(f"  Analytical transmission: {comparison['analytical_transmission']:.6f}")
    print(f"  Monte Carlo transmission: {comparison['mc_transmission']:.6f}")
    print(f"  Buildup factor: {comparison['buildup_factor']:.3f}")


def example_energy_dependence():
    """Example 3: Study energy dependence of shielding."""
    print("\n" + "=" * 70)
    print("Example 3: Energy Dependence of Lead Shield")
    print("=" * 70)

    # Create simulator with 2 cm lead
    sim = MonteCarloShieldSimulator(seed=42)
    sim.add_layer(
        material_name="Lead",
        thickness_cm=2.0,
        mu_total=0.77,
        mu_compton=0.58,
        mu_photoelectric=0.19,
        density_g_cm3=11.34
    )

    # Test different energies
    energies = [0.5, 1.0, 2.0, 3.0]  # MeV
    n_photons = 200_000

    print(f"\nTesting {len(energies)} different energies with {n_photons:,} photons each...\n")
    print(f"{'Energy (MeV)':<15} {'Transmission':<15} {'Buildup':<15} {'Transmitted':<15}")
    print("-" * 60)

    for energy in energies:
        result = sim.run(source_energy_MeV=energy, num_photons=n_photons)
        print(f"{energy:<15.1f} {result.transmission_factor:<15.6f} "
              f"{result.buildup_factor:<15.3f} {result.transmitted_photons:<15,d}")

    print("\nNote: Higher energy photons are more penetrating, but buildup")
    print("      factors also change with energy due to different interaction")
    print("      cross-sections.")


def example_dict_interface():
    """Example 4: Using dictionary interface (compatible with existing API)."""
    print("\n" + "=" * 70)
    print("Example 4: Dictionary Interface (compatible with shield_lite API)")
    print("=" * 70)

    # Create simulator
    sim = MonteCarloShieldSimulator(seed=42)

    # Define materials using dictionaries (like the existing shield_lite API)
    thicknesses = {
        'Lead': 3.0,
        'Steel': 2.0
    }

    mu_total = {
        'Lead': 0.77,
        'Steel': 0.47
    }

    mu_compton = {
        'Lead': 0.58,
        'Steel': 0.35
    }

    mu_photoelectric = {
        'Lead': 0.19,
        'Steel': 0.12
    }

    density = {
        'Lead': 11.34,
        'Steel': 7.85
    }

    # Add layers from dictionaries
    sim.add_layers_from_dict(
        thicknesses=thicknesses,
        mu_total=mu_total,
        mu_compton=mu_compton,
        mu_photoelectric=mu_photoelectric,
        density=density
    )

    # Run simulation
    result = sim.run(source_energy_MeV=1.0, num_photons=200_000)

    print(f"\nResults:")
    print(f"  Transmission: {result.transmission_factor:.6f}")
    print(f"  Buildup factor: {result.buildup_factor:.3f}")
    print(f"\nThis interface is compatible with the existing shield_lite")
    print(f"dose() and mass() functions for easy integration!")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Monte Carlo Gamma Ray Shielding Simulation Examples")
    print("=" * 70)

    try:
        example_simple_lead_shield()
        example_multilayer_shield()
        example_energy_dependence()
        example_dict_interface()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

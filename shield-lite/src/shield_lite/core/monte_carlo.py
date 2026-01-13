"""
Monte Carlo photon transport simulation for gamma ray shielding.

This module provides a high-level Python interface to the C++ Monte Carlo
simulation engine that models realistic photon transport through multi-layer
shields, including Compton scattering and photoelectric absorption.
"""

from typing import Dict, List, Optional
import numpy as np

try:
    from shield_lite._monte_carlo import MonteCarloSimulator, MonteCarloResult
except ImportError as e:
    raise ImportError(
        "C++ Monte Carlo module not found. Please compile the C++ extension:\n"
        "  cd <project-root>\n"
        "  mkdir build && cd build\n"
        "  cmake .. && make\n"
        f"Original error: {e}"
    )


class MonteCarloShieldSimulator:
    """
    High-level interface for Monte Carlo gamma ray shielding simulation.

    This class provides a convenient Python interface to run Monte Carlo
    simulations of photon transport through multi-layer shields. It accounts
    for realistic physics including Compton scattering, photoelectric absorption,
    and calculates the dose buildup factor.

    Attributes
    ----------
    simulator : MonteCarloSimulator
        The underlying C++ simulator instance

    Examples
    --------
    >>> sim = MonteCarloShieldSimulator(seed=42)
    >>> sim.add_layer("Lead", thickness_cm=5.0, mu_total=0.8,
    ...               mu_compton=0.5, mu_photoelectric=0.3, density=11.34)
    >>> result = sim.run(source_energy_MeV=1.0, num_photons=100000)
    >>> print(f"Transmission: {result.transmission_factor:.4f}")
    >>> print(f"Buildup factor: {result.buildup_factor:.2f}")
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the Monte Carlo simulator.

        Parameters
        ----------
        seed : int, optional
            Random seed for reproducibility. If None, uses default seed (42).
        """
        if seed is None:
            self.simulator = MonteCarloSimulator()
        else:
            self.simulator = MonteCarloSimulator(seed)
        self._layers_info = []

    def add_layer(self,
                  material_name: str,
                  thickness_cm: float,
                  mu_total: float,
                  mu_compton: float,
                  mu_photoelectric: float,
                  density_g_cm3: float) -> None:
        """
        Add a material layer to the shield.

        Parameters
        ----------
        material_name : str
            Name of the material (e.g., "Lead", "Concrete", "Steel")
        thickness_cm : float
            Thickness of the layer in cm
        mu_total : float
            Total linear attenuation coefficient in cm^-1
        mu_compton : float
            Compton scattering coefficient in cm^-1
        mu_photoelectric : float
            Photoelectric absorption coefficient in cm^-1
        density_g_cm3 : float
            Material density in g/cm^3

        Notes
        -----
        Layers are added in order from source to detector. The first layer
        added will be closest to the source.
        """
        self.simulator.add_layer(
            material_name, thickness_cm, mu_total,
            mu_compton, mu_photoelectric, density_g_cm3
        )
        self._layers_info.append({
            'material': material_name,
            'thickness_cm': thickness_cm,
            'mu_total': mu_total,
            'mu_compton': mu_compton,
            'mu_photoelectric': mu_photoelectric,
            'density_g_cm3': density_g_cm3
        })

    def add_layers_from_dict(self,
                            thicknesses: Dict[str, float],
                            mu_total: Dict[str, float],
                            mu_compton: Dict[str, float],
                            mu_photoelectric: Dict[str, float],
                            density: Dict[str, float]) -> None:
        """
        Add multiple layers from dictionaries (compatible with existing shield_lite API).

        Parameters
        ----------
        thicknesses : dict
            Dictionary mapping material names to thicknesses (cm)
        mu_total : dict
            Dictionary mapping material names to total attenuation coefficients (cm^-1)
        mu_compton : dict
            Dictionary mapping material names to Compton coefficients (cm^-1)
        mu_photoelectric : dict
            Dictionary mapping material names to photoelectric coefficients (cm^-1)
        density : dict
            Dictionary mapping material names to densities (g/cm^3)

        Examples
        --------
        >>> sim = MonteCarloShieldSimulator()
        >>> sim.add_layers_from_dict(
        ...     thicknesses={'Lead': 5.0, 'Steel': 2.0},
        ...     mu_total={'Lead': 0.8, 'Steel': 0.6},
        ...     mu_compton={'Lead': 0.5, 'Steel': 0.4},
        ...     mu_photoelectric={'Lead': 0.3, 'Steel': 0.2},
        ...     density={'Lead': 11.34, 'Steel': 7.85}
        ... )
        """
        for material in thicknesses.keys():
            self.add_layer(
                material,
                thicknesses[material],
                mu_total[material],
                mu_compton[material],
                mu_photoelectric[material],
                density[material]
            )

    def clear_layers(self) -> None:
        """Remove all layers from the shield configuration."""
        self.simulator.clear_layers()
        self._layers_info.clear()

    def run(self,
            source_energy_MeV: float,
            num_photons: int = 100000,
            source_area_cm2: float = 1.0) -> MonteCarloResult:
        """
        Run the Monte Carlo simulation.

        Parameters
        ----------
        source_energy_MeV : float
            Energy of the gamma ray source in MeV
        num_photons : int, optional
            Number of photons to simulate (default: 100000)
            Higher values give better statistics but take longer
        source_area_cm2 : float, optional
            Source area in cm^2 (default: 1.0)

        Returns
        -------
        MonteCarloResult
            Simulation results containing:
            - dose_transmitted: Average energy transmitted per photon (MeV)
            - dose_absorbed: Average energy absorbed per photon (MeV)
            - transmission_factor: Fraction of photons transmitted (0 to 1)
            - buildup_factor: Dose buildup factor (>1 due to scattering)
            - uncertainty: Statistical uncertainty
            - total_photons: Number of photons simulated
            - transmitted_photons: Number of photons that passed through

        Raises
        ------
        RuntimeError
            If no layers have been added to the shield

        Notes
        -----
        The buildup factor represents the ratio of the actual dose to the
        dose that would be calculated using simple exponential attenuation.
        It accounts for scattered photons and is always >= 1.

        Typical values: 100,000-1,000,000 photons for accurate results.
        """
        if self.simulator.get_num_layers() == 0:
            raise ValueError("No layers added to shield. Use add_layer() first.")

        return self.simulator.run(source_energy_MeV, num_photons, source_area_cm2)

    def get_shield_info(self) -> List[Dict]:
        """
        Get information about the current shield configuration.

        Returns
        -------
        list of dict
            List of dictionaries containing information about each layer
        """
        return self._layers_info.copy()

    def get_total_thickness(self) -> float:
        """
        Calculate the total thickness of the shield.

        Returns
        -------
        float
            Total thickness in cm
        """
        return sum(layer['thickness_cm'] for layer in self._layers_info)

    def compare_with_analytical(self,
                               source_energy_MeV: float,
                               num_photons: int = 100000) -> Dict:
        """
        Run Monte Carlo simulation and compare with analytical exponential model.

        This is useful for validating the simulation and understanding the
        importance of the buildup factor.

        Parameters
        ----------
        source_energy_MeV : float
            Energy of the gamma ray source in MeV
        num_photons : int, optional
            Number of photons to simulate (default: 100000)

        Returns
        -------
        dict
            Dictionary containing:
            - 'monte_carlo': Monte Carlo result object
            - 'analytical_transmission': Simple exponential prediction
            - 'buildup_factor': Ratio of MC to analytical
            - 'difference_percent': Percentage difference
        """
        # Run Monte Carlo
        mc_result = self.run(source_energy_MeV, num_photons)

        # Calculate analytical prediction (simple Beer-Lambert law)
        total_mu_thickness = sum(
            layer['mu_total'] * layer['thickness_cm']
            for layer in self._layers_info
        )
        analytical_transmission = np.exp(-total_mu_thickness)

        # Calculate difference
        if analytical_transmission > 0:
            buildup = mc_result.transmission_factor / analytical_transmission
            difference_percent = (
                (mc_result.transmission_factor - analytical_transmission)
                / analytical_transmission * 100
            )
        else:
            buildup = float('inf')
            difference_percent = float('inf')

        return {
            'monte_carlo': mc_result,
            'analytical_transmission': analytical_transmission,
            'buildup_factor': buildup,
            'difference_percent': difference_percent,
            'mc_transmission': mc_result.transmission_factor,
            'mc_uncertainty': mc_result.uncertainty
        }


def estimate_required_photons(desired_uncertainty: float = 0.01,
                             expected_transmission: float = 0.1) -> int:
    """
    Estimate the number of photons needed for a given statistical uncertainty.

    Parameters
    ----------
    desired_uncertainty : float, optional
        Desired relative uncertainty (default: 0.01 = 1%)
    expected_transmission : float, optional
        Expected transmission factor (default: 0.1 = 10%)

    Returns
    -------
    int
        Recommended number of photons to simulate

    Notes
    -----
    This uses the statistical formula: uncertainty ~ 1/sqrt(N_detected)
    where N_detected = N_total * transmission_factor
    """
    # Statistical uncertainty scales as 1/sqrt(N_detected)
    # N_detected = N_total * transmission
    # uncertainty = 1/sqrt(N_total * transmission)
    # Solve for N_total:
    n_total = int((1.0 / (desired_uncertainty**2 * expected_transmission)) * 1.5)
    return max(10000, n_total)  # Minimum 10,000 photons

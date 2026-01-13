# This file initializes the core module of the package.

from .dose import dose
from .mass import mass

# Monte Carlo module (requires C++ compilation)
try:
    from .monte_carlo import MonteCarloShieldSimulator, estimate_required_photons
    __all__ = ['dose', 'mass', 'MonteCarloShieldSimulator', 'estimate_required_photons']
except ImportError:
    # C++ module not compiled yet
    __all__ = ['dose', 'mass']
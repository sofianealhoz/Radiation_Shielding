# Shield-Lite

Shield-Lite is a Python package designed for the design and analysis of multi-layer shields against mono-energetic gamma sources. It provides tools for dose and mass calculations, least squares calibration, and optimization through grid search, all accessible via a command-line interface (CLI). The package also includes visualization capabilities for better understanding the results.

## Features

- **Dose Calculation**: Calculate the dose behind a shield based on material properties and thicknesses.
- **Mass Calculation**: Determine the mass of the shield based on thicknesses and densities.
- **Calibration**: Perform least squares calibration for source intensity and effective attenuation coefficient.
- **Optimization**: Use grid search to find optimal thicknesses that meet dose constraints with minimal mass.
- **Visualization**: Generate plots for dose, residuals, and Pareto frontiers.

## Installation

To install Shield-Lite, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/shield-lite.git
cd shield-lite
pip install -e .
```

## Usage

You can use the Shield-Lite CLI to perform various calculations and optimizations. Here are some example commands:

```bash
# Calculate dose
python -m shield_lite.cli dose --thicknesses '{"lead": 10, "water": 20}' --mu '{"lead": 0.1, "water": 0.05}' --S 1.0

# Perform grid search
python -m shield_lite.cli grid-search --order '["lead", "water"]' --ranges '{"lead": "0-50", "water": "0-50"}' --Dmax 1.0
```

## Examples

Example configurations and materials can be found in the `examples` directory:

- `config.yaml`: Example case study parameters.
- `materials.csv`: Example material data.
- `example_usage.py`: Example usage of the Shield-Lite package.

## Testing

To run the tests for Shield-Lite, use pytest:

```bash
pytest tests/
```



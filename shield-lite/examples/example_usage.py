# example_usage.py

from shield_lite.core.dose import dose
from shield_lite.core.mass import mass
from shield_lite.optimization.grid_search import grid_search
import yaml
import pandas as pd

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def load_materials(materials_path):
    return pd.read_csv(materials_path)

def main():
    config = load_config('examples/config.yaml')
    materials = load_materials('examples/materials.csv')

    thicknesses = config['thicknesses']
    mu = {material['name']: material['mu'] for _, material in materials.iterrows()}
    rho = {material['name']: material['rho'] for _, material in materials.iterrows()}
    S = config['source_intensity']
    Dmax = config['dose_constraint']
    area_m2 = config.get('area_m2', 1.0)

    calculated_dose = dose(thicknesses, mu, S)
    calculated_mass = mass(thicknesses, rho, area_m2)

    print(f"Calculated Dose: {calculated_dose} Gy")
    print(f"Calculated Mass: {calculated_mass} kg")

    optimal_thicknesses = grid_search(list(thicknesses.keys()), config['ranges_mm'], mu, rho, S, Dmax, area_m2)
    print(f"Optimal Thicknesses: {optimal_thicknesses}")

if __name__ == "__main__":
    main()
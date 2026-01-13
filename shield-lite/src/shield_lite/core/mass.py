def mass(thicknesses: dict[str, float], rho: dict[str, float], area_m2: float = 1.0) -> float:
    total_mass = 0.0
    for material, thickness in thicknesses.items():
        if material in rho:
            total_mass += rho[material] * thickness * area_m2
        else:
            raise ValueError(f"Density for material '{material}' not found.")
    return total_mass
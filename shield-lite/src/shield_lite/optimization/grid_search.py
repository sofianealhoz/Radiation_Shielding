# filepath: 
import numpy as np
from itertools import product
from typing import List, Dict, Any
from shield_lite.core.shield import Shield, Material, Source

def parse_range(range_str: str) -> np.ndarray:
    """
    Parse une chaîne de caractères définissant une plage.
    Formats supportés :
    - "start..end..step" (ex: "0..10..1") -> np.arange
    - "start,end,n_points" (ex: "0,10,5") -> np.linspace
    - "start,end" (ex: "0,10") -> np.linspace(start, end, 5) (par défaut)
    """
    if ".." in range_str:
        parts = [float(x) for x in range_str.split("..")]
        start, end = parts[0], parts[1]
        step = parts[2] if len(parts) > 2 else 1.0
        # arange exclut la fin, on ajoute un petit epsilon pour l'inclure si besoin
        return np.arange(start, end + step/1000.0, step)
    else:
        parts = [float(x) for x in range_str.split(",")]
        start, end = parts[0], parts[1]
        num = int(parts[2]) if len(parts) > 2 else 5
        return np.linspace(start, end, num)

def grid_search(
    order: List[str],
    ranges_str: Dict[str, str],
    materials_db: Dict[str, Material],
    source: Source,  # <--- Changement ici : Type Source au lieu de float
    Dmax: float,
    area_m2: float = 1.0,
    topk: int = 5
) -> List[Dict[str, Any]]:
    """
    Effectue une recherche par grille en utilisant les objets Shield Material et Source.
    """
    
    # 1. Génération des grilles d'épaisseurs pour chaque matériau
    # ex: {'Lead': [0, 1, 2...], 'Concrete': [10, 20...]}
    thickness_grids = {}
    for mat_name in order:
        if mat_name not in ranges_str:
            raise ValueError(f"Pas de plage définie pour {mat_name}")
        thickness_grids[mat_name] = parse_range(ranges_str[mat_name])

    # 2. Produit Cartésien (toutes les combinaisons possibles)
    # keys: ['Lead', 'Concrete']
    # values: [(0, 10), (0, 20), (1, 10)...]
    keys = list(thickness_grids.keys())
    all_combinations = product(*thickness_grids.values())

    valid_results = []

    # 3. Boucle de simulation
    for values in all_combinations:
        # Création d'un dictionnaire temporaire {Mat: Epaisseur}
        current_thicknesses = dict(zip(keys, values))
        
        # Construction du bouclier objet
        shield = Shield()
        for mat_name, t_mm in current_thicknesses.items():
            if mat_name not in materials_db:
                raise ValueError(f"Matériau inconnu: {mat_name}")
            
            mat_obj = materials_db[mat_name]
            shield.add_layer(mat_obj, t_mm)

        # Calculs physiques via la classe Shield
        dose_val = shield.calculate_dose(source)

        # Vérification de la contrainte
        if dose_val <= Dmax:
            mass_val = shield.calculate_total_mass(area_m2)
            
            valid_results.append({
                "thicknesses": current_thicknesses,
                "dose": dose_val,
                "mass": mass_val,
                "shield_obj": shield # Optionnel : garder l'objet pour inspection
            })

    # 4. Tri par masse croissante (le plus léger en premier)
    valid_results.sort(key=lambda x: x["mass"])

    return valid_results[:topk]
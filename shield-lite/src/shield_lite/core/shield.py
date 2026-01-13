import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
from pyne import material as pyne_mat
from pyne import data as pyne_data

@dataclass
class Source:
    """
    Représente une source radioactive.
    """
    intensity: float  # Intensité S initiale (Bq)
    energy_MeV: float = 1.0
    name: str = "Unknown Source"
    isotope: Optional[str] = None  # Nouveau champ: ex "Co60", "Sr90"

    def decay(self, time_elapsed: float, half_life: float = None) -> float:
        """
        Calcule l'intensité restante après un certain temps.
        
        Si PyNE est disponible et que 'isotope' est défini, utilise les chaînes de Bateman.
        Sinon, utilise la loi exponentielle simple (nécessite half_life).
        """
        # 1. Méthode PyNE (Précise, avec filiation)
        if HAS_PYNE and self.isotope:
            try:
                # a. Créer un matériau pur (100% de l'isotope)
                # On commence avec 1 gramme arbitraire pour calculer l'activité spécifique
                mat_ref = pyne_mat.Material({self.isotope: 1.0})
                
                # b. Calculer la masse nécessaire pour avoir l'intensité initiale S
                # activity() renvoie des Bq par défaut
                ref_activity = mat_ref.activity() 
                if ref_activity == 0:
                    return 0.0
                
                mass_needed = self.intensity / ref_activity
                
                # c. Créer la source réelle avec la bonne masse
                real_source = mat_ref * mass_needed
                
                # d. Appliquer la décroissance (time_elapsed en secondes)
                # PyNE renvoie un NOUVEAU matériau avec la composition après temps t
                decayed_source = real_source.decay(time_elapsed)
                
                # e. Retourner l'activité totale (Père + Fils)
                return decayed_source.activity()
                
            except Exception as e:
                print(f"Attention: Erreur calcul décroissance PyNE ({e}). Repli sur méthode simple.")

        # 2. Méthode Simple (Repli)
        if half_life is not None and half_life > 0:
            return self.intensity * (0.5 ** (time_elapsed / half_life))
        
        # Si on ne peut rien faire
        return self.intensity

@dataclass
class Material:
    """
    Représente un matériau avec ses propriétés physiques.
    """
    name: str
    mu: float       # Coefficient d'atténuation linéaire (cm^-1)
    density: float  # Masse volumique (g/cm^3)

    @staticmethod
    def load_from_csv(filepath: str) -> Dict[str, 'Material']:
        """
        Charge une base de données de matériaux depuis un CSV.
        Retourne un dictionnaire {nom_materiau: ObjetMaterial}.
        """
        df = pd.read_csv(filepath)
        materials = {}
        for _, row in df.iterrows():
            # Adaptation aux noms de colonnes de votre CSV actuel
            mat = Material(
                name=row['material'],
                mu=row['mu_cm1'],
                density=row['density_g_cm3']
            )
            materials[mat.name] = mat
        return materials
    
    @staticmethod
    def load_from_pyne(names: List[str], energy_MeV: float) -> Dict[str, 'Material']:
        """
        Charge les matériaux en utilisant la base de données nucléaire PyNE.
        Calcule automatiquement mu pour l'énergie donnée.
        """
        if not HAS_PYNE:
            raise ImportError("PyNE n'est pas installé. Veuillez l'installer ou utiliser le CSV.")

        materials = {}
        print(f"--- Interrogation de PyNE (Energy={energy_MeV} MeV) ---")
        
        for name in names:
            try:
                # 1. Création du matériau PyNE (reconnaît "Steel", "H2O", "Fe", etc.)
                pm = pyne_mat.Material(name)
                
                # 2. Récupération de la densité (g/cm3)
                rho = pm.density
                
                # 3. Calcul du mu linéaire (cm^-1)
                # Formule : mu_lin = rho * sum(w_i * (mu/rho)_i)
                # pyne.data.mu_gamma(nuc, E) donne le coeff d'atténuation massique (cm^2/g)
                
                mass_att_coeff_mix = 0.0
                comp = pm.mult_by_mass() # Composition massique {nuc_id: fraction}

                for nuc_id, weight_frac in comp.items():
                    # mu_gamma attend l'énergie en MeV
                    try:
                        mu_mass_i = pyne_data.mu_gamma(nuc_id, energy_MeV)
                        mass_att_coeff_mix += weight_frac * mu_mass_i
                    except Exception:
                        # Si pas de données pour un isotope mineur, on ignore (ou log warning)
                        pass

                mu_linear = mass_att_coeff_mix * rho
                
                # Création de NOTRE objet Material
                materials[name] = Material(name=name, mu=mu_linear, density=rho)
                print(f"  > {name}: rho={rho:.2f}, mu={mu_linear:.4f} cm-1")

            except Exception as e:
                print(f"  /!\\ Erreur PyNE pour '{name}': {e}")
        
        return materials

@dataclass
class Layer:
    """
    Représente une couche physique du bouclier.
    """
    material: Material
    thickness_mm: float

    @property
    def thickness_cm(self) -> float:
        return self.thickness_mm / 10.0

    def transmission(self) -> float:
        """Calcule le facteur de transmission (I/I0) de cette couche."""
        return np.exp(-self.material.mu * self.thickness_cm)

    def mass(self, area_m2: float) -> float:
        """Calcule la masse de la couche en kg."""
        # Volume en cm3 = Area (m2 -> cm2) * thickness (cm)
        area_cm2 = area_m2 * 10000
        volume_cm3 = area_cm2 * self.thickness_cm
        mass_g = volume_cm3 * self.material.density
        return mass_g / 1000.0  # Conversion g -> kg

class Shield:
    """
    Représente un bouclier multicouche complet.
    """
    def __init__(self, layers: Optional[List[Layer]] = None):
        self.layers = layers if layers is not None else []

    def add_layer(self, material: Material, thickness_mm: float):
        self.layers.append(Layer(material, thickness_mm))

    def calculate_dose(self, source: Source) -> float:
        """
        Calcule la dose transmise à travers toutes les couches pour une source donnée.
        Formule: D = S * exp(-sum(mu_i * t_i))
        """
        transmission_total = 1.0
        for layer in self.layers:
            transmission_total *= layer.transmission()
        return source.intensity * transmission_total

    def calculate_total_mass(self, area_m2: float = 1.0) -> float:
        """Calcule la masse totale du bouclier en kg."""
        return sum(layer.mass(area_m2) for layer in self.layers)

    def __repr__(self):
        desc = " | ".join([f"{l.material.name}({l.thickness_mm}mm)" for l in self.layers])
        return f"<Shield: [{desc}]>"
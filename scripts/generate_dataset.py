import pandas as pd
import numpy as np
import random
import uuid
import os
import time

from sqlalchemy import create_engine
from shield_lite.core import MonteCarloShieldSimulator
# On importe les modèles pour être sûr que SQLAlchemy puisse créer les tables si elles manquent
from api.models import Base

# Connexion BDD
DB_URL = os.getenv("DATABASE_URL", "postgresql://shield_user:shield_pass@db:5432/shield_db")
engine = create_engine(DB_URL)

MATERIALS = [
    {"name": "Lead", "mu_total": 0.77, "mu_compton": 0.58, "mu_photo": 0.19, "rho": 11.34},
    {"name": "Concrete", "mu_total": 0.16, "mu_compton": 0.12, "mu_photo": 0.04, "rho": 2.3},
    {"name": "Steel", "mu_total": 0.47, "mu_compton": 0.35, "mu_photo": 0.12, "rho": 7.85},
    {"name": "Water", "mu_total": 0.07, "mu_compton": 0.07, "mu_photo": 0.00, "rho": 1.0},
]

def generate_batch(n_samples=50):
    print(f"🚀 Génération de {n_samples} simulations (Mode Relationnel SQL)...")
    
    # Listes pour stocker les données avant création des DataFrames
    simulations_data = []
    layers_data = []

    start_global = time.time()

    for i in range(n_samples):
        # 1. Préparation de la simulation
        sim_id = str(uuid.uuid4()) # On génère l'ID tout de suite pour lier les tables
        energy = round(random.uniform(0.5, 5.0), 2)
        photons = 2000 # Nombre bas pour aller vite
        
        n_layers = random.randint(1, 4)
        
        sim = MonteCarloShieldSimulator(seed=i)

        # 2. Boucle sur les couches (Remplissage table Enfant)
        for order_idx in range(n_layers):
            mat = random.choice(MATERIALS)
            thickness = round(random.uniform(1.0, 15.0), 1)

            # Ajout au moteur physique C++
            sim.add_layer(
                mat["name"], thickness, mat["mu_total"],
                mat["mu_compton"], mat["mu_photo"], mat["rho"]
            )

            # Ajout à la liste des données pour la table 'simulation_layers'
            layers_data.append({
                "simulation_id": sim_id,   # LA CLE ETRANGERE
                "order_index": order_idx,  # Position de la couche (0, 1, 2...)
                "material": mat["name"],
                "thickness_cm": thickness,
                "density": mat["rho"]
            })

        # 3. Exécution du calcul
        try:
            result = sim.run(source_energy_MeV=energy, num_photons=photons)

            # 4. Ajout à la liste des données pour la table 'simulations'
            simulations_data.append({
                "id": sim_id,
                "energy_mev": energy,
                "photons": photons,
                "transmission": result.transmission_factor,
                "buildup_factor": result.buildup_factor,
                "dose_transmitted": result.dose_transmitted,
                "uncertainty": result.uncertainty,
                "status": "COMPLETED",
                "created_at": pd.Timestamp.now()
            })
            
        except Exception as e:
            print(f"❌ Erreur sur simulation {i}: {e}")

    # 5. Création des DataFrames Pandas
    df_simulations = pd.DataFrame(simulations_data)
    df_layers = pd.DataFrame(layers_data)

    print(f"📊 Données générées : {len(df_simulations)} Simulations, {len(df_layers)} Couches.")

    # 6. Insertion en Base (Séquentielle)
    if not df_simulations.empty:
        # Création des tables si elles n'existent pas (Important !)
        Base.metadata.create_all(bind=engine)

        print("💾 Insertion table 'simulations'...")
        df_simulations.to_sql(
            "simulations",
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000
        )

        print("💾 Insertion table 'simulation_layers'...")
        df_layers.to_sql(
            "simulation_layers",
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000
        )
        
        duration = time.time() - start_global
        print(f"✅ Terminé en {duration:.2f} secondes !")

    else:
        print("⚠️ Aucune donnée générée.")

if __name__ == "__main__":
    generate_batch()
from shield_lite.core.shield import Shield, Material
import pandas as pd

def main():
    csv_path = "examples/materials.csv"
    print(f"--- Chargement des matériaux via Pandas depuis {csv_path} ---")
    
    # Cette méthode statique utilise pd.read_csv() en interne
    materials_db = Material.load_from_csv(csv_path)
    
    print(f"Matériaux chargés : {list(materials_db.keys())}")

    # Création d'un bouclier vide
    my_shield = Shield()

    # Vérification que les matériaux existent avant de les utiliser
    if "Lead" in materials_db and "Concrete" in materials_db:
        lead = materials_db["Lead"]
        concrete = materials_db["Concrete"]

        # Ajout de couches (Composition)
        my_shield.add_layer(lead, thickness_mm=10)      # 10mm de Plomb
        my_shield.add_layer(concrete, thickness_mm=50)  # 50mm de Béton

        print(f"\nConfiguration du bouclier : {my_shield}")

        # Paramètres de simulation
        S_source = 100.0  # Intensité source arbitraire
        area = 1.0        # Surface 1m2

        # Calculs physiques via les méthodes de la classe Shield
        dose = my_shield.calculate_dose(S=S_source)
        mass = my_shield.calculate_total_mass(area_m2=area)

        print(f"\n--- Résultats de la simulation ---")
        print(f"Source Initiale : {S_source}")
        print(f"Dose Transmise  : {dose:.4f}")
        print(f"Masse Totale    : {mass:.2f} kg")

        # Test dynamique : ajout d'une couche supplémentaire
        if "Steel" in materials_db:
            print("\n--- Modification : Ajout d'une couche d'acier (20mm) ---")
            steel = materials_db["Steel"]
            my_shield.add_layer(steel, thickness_mm=20)
            
            new_dose = my_shield.calculate_dose(S=S_source)
            print(f"Nouvelle Dose   : {new_dose:.4f}")
            print(f"Gain protection : {(1 - new_dose/dose)*100:.1f}%")
    else:
        print("Erreur : Les matériaux 'Lead' ou 'Concrete' sont introuvables dans le CSV.")

if __name__ == "__main__":
    main()
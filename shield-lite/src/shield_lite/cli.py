from typer import Typer, Option
from shield_lite.core.dose import dose
from shield_lite.core.mass import mass
from shield_lite.optimization.calibration import fit_S, fit_S_mu_eff
from shield_lite.optimization.grid_search import grid_search

app = Typer()


@app.command()
def optimize(
    materials: List[str] = Argument(..., help="Liste des matériaux (ex: Lead Concrete)"),
    ranges: List[str] = Option(..., help="Plages pour chaque matériau (start end step). Il faut 3 valeurs par matériau."),
    csv: str = Option("examples/materials.csv", help="Chemin vers le fichier materials.csv"),
    use_pyne: bool = Option(False, "--pyne", help="Utiliser PyNE pour récupérer les données nucléaires au lieu du CSV"),
    S: float = Option(..., help="Intensité de la source"),
    Dmax: float = Option(..., help="Dose maximale autorisée"),
    area: float = Option(1.0, help="Surface du bouclier en m2"),
    topk: int = Option(5, help="Nombre de solutions à afficher")
):
    """
    Optimise le bouclier en trouvant la combinaison la plus légère.
    Exemple: python -m shield_lite.cli optimize Lead Concrete --ranges 0 10 1 0 50 5 --S 100 --Dmax 0.5
    """
    
    # 1. Validation des entrées
    if len(ranges) != len(materials) * 3:
        print(f"Erreur : Vous avez fourni {len(materials)} matériaux, il faut donc {len(materials) * 3} valeurs de plage (start, end, step).")
        print(f"Reçu : {len(ranges)} valeurs.")
        return

    # 2. Reconstruction du dictionnaire de plages (ranges_str)
    # On transforme la liste plate [0, 10, 1, 0, 50, 5] en dictionnaire
    # {"Lead": "0..10..1", "Concrete": "0..50..5"}
    ranges_dict = {}
    for i, mat_name in enumerate(materials):
        start = ranges[i*3]
        end = ranges[i*3 + 1]
        step = ranges[i*3 + 2]
        ranges_dict[mat_name] = f"{start}..{end}..{step}"

    print(f"--- Configuration ---")
    print(f"Matériaux : {materials}")
    print(f"Plages    : {ranges_dict}")

    # 3. Chargement des données (Objets)
    try:
        if use_pyne:
            print(f"Mode: PyNE (Calcul dynamique des mu pour {energy} MeV)")
            # On passe la liste des noms demandés par l'utilisateur
            materials_db = Material.load_from_pyne(materials, energy_MeV=energy)
        else:
            print(f"Mode: CSV ({csv})")
            materials_db = Material.load_from_csv(csv)
        source_obj = Source(intensity=S)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {csv} est introuvable.")
        return

    # 4. Vérification que les matériaux demandés existent dans le CSV
    missing = [m for m in materials if m not in materials_db]
    if missing:
        print(f"Erreur : Les matériaux suivants ne sont pas dans le CSV : {missing}")
        print(f"Disponibles : {list(materials_db.keys())}")
        return

    # 5. Lancement de la recherche
    print("--- Démarrage de l'optimisation ---")
    try:
        results = grid_search(
            order=materials,
            ranges_str=ranges_dict,
            materials_db=materials_db,
            source=source_obj,
            Dmax=Dmax,
            area_m2=area,
            topk=topk
        )

        if not results:
            print("Aucune solution trouvée respectant la contrainte de dose.")
            return

        print(f"\nTop {len(results)} solutions trouvées :")
        print(f"{'Masse (kg)':<12} | {'Dose':<10} | {'Configuration'}")
        print("-" * 60)
        for res in results:
            config = ", ".join([f"{k}={v}mm" for k,v in res['thicknesses'].items()])
            print(f"{res['mass']:<12.2f} | {res['dose']:<10.4f} | {config}")

    except Exception as e:
        print(f"Erreur critique : {e}")

if __name__ == "__main__":
    app()
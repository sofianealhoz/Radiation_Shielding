# Monte Carlo Photon Transport Simulation (C++)

## Vue d'ensemble

Ce module ajoute une simulation Monte Carlo de transport de photons gamma en C++ au projet `shield-lite`. Il simule de manière réaliste le transport des photons à travers un blindage multicouche en tenant compte des interactions physiques :

- **Diffusion Compton** : Les photons sont diffusés et perdent de l'énergie
- **Absorption photoélectrique** : Les photons sont complètement absorbés
- **Facteur de buildup** : Calcul de l'accumulation de dose due aux photons diffusés

## Pourquoi Monte Carlo ?

Les calculs analytiques existants (`dose.py`) utilisent une loi d'atténuation exponentielle simple qui ne tient pas compte des photons diffusés. La simulation Monte Carlo :

1. **Plus réaliste** : Modélise les trajectoires individuelles des photons
2. **Calcule le buildup factor** : Ratio entre dose réelle et dose prédite par l'exponentielle
3. **Rapide** : Implémentation C++ optimisée pour simuler des millions de photons
4. **Flexible** : Supporte des géométries multicouches complexes

## Installation

### Prérequis

```bash
# Sur Ubuntu/Debian
sudo apt-get install cmake g++ python3-dev

# Sur macOS (avec Homebrew)
brew install cmake pybind11

# Sur Fedora/RHEL
sudo dnf install cmake gcc-c++ python3-devel
```

### Compilation

1. **Installer pybind11** (si ce n'est pas déjà fait) :
```bash
cd shield-lite
poetry install  # Installe pybind11 via pyproject.toml
```

2. **Compiler le module C++** :
```bash
cd shield-lite
mkdir -p build
cd build
cmake ..
make -j$(nproc)  # Compile en parallèle
cd ..
```

3. **Vérifier l'installation** :
```bash
python -c "from shield_lite.core import MonteCarloShieldSimulator; print('OK')"
```

## Utilisation

### Exemple simple

```python
from shield_lite.core import MonteCarloShieldSimulator

# Créer le simulateur
sim = MonteCarloShieldSimulator(seed=42)

# Ajouter une couche de plomb (5 cm)
sim.add_layer(
    material_name="Lead",
    thickness_cm=5.0,
    mu_total=0.77,          # Coefficient d'atténuation total (cm^-1)
    mu_compton=0.58,        # Coefficient de Compton (cm^-1)
    mu_photoelectric=0.19,  # Coefficient photoélectrique (cm^-1)
    density_g_cm3=11.34     # Densité (g/cm^3)
)

# Lancer la simulation
result = sim.run(
    source_energy_MeV=1.0,   # Énergie de la source (MeV)
    num_photons=100_000      # Nombre de photons à simuler
)

# Afficher les résultats
print(f"Transmission: {result.transmission_factor:.4f}")
print(f"Buildup factor: {result.buildup_factor:.2f}")
print(f"Photons transmis: {result.transmitted_photons}/{result.total_photons}")
```

### Exemple multicouche

```python
sim = MonteCarloShieldSimulator(seed=42)

# Couche 1 : Plomb (près de la source)
sim.add_layer("Lead", thickness_cm=3.0, mu_total=0.77,
              mu_compton=0.58, mu_photoelectric=0.19, density_g_cm3=11.34)

# Couche 2 : Béton (milieu)
sim.add_layer("Concrete", thickness_cm=10.0, mu_total=0.16,
              mu_compton=0.12, mu_photoelectric=0.04, density_g_cm3=2.3)

# Couche 3 : Acier (extérieur)
sim.add_layer("Steel", thickness_cm=2.0, mu_total=0.47,
              mu_compton=0.35, mu_photoelectric=0.12, density_g_cm3=7.85)

result = sim.run(source_energy_MeV=1.0, num_photons=500_000)
print(f"Buildup factor: {result.buildup_factor:.2f}")
```

### Interface compatible avec l'API existante

```python
# Utiliser des dictionnaires (comme dose() et mass())
sim = MonteCarloShieldSimulator()

thicknesses = {'Lead': 3.0, 'Steel': 2.0}
mu_total = {'Lead': 0.77, 'Steel': 0.47}
mu_compton = {'Lead': 0.58, 'Steel': 0.35}
mu_photoelectric = {'Lead': 0.19, 'Steel': 0.12}
density = {'Lead': 11.34, 'Steel': 7.85}

sim.add_layers_from_dict(
    thicknesses=thicknesses,
    mu_total=mu_total,
    mu_compton=mu_compton,
    mu_photoelectric=mu_photoelectric,
    density=density
)

result = sim.run(source_energy_MeV=1.0, num_photons=200_000)
```

### Comparaison avec le modèle analytique

```python
sim = MonteCarloShieldSimulator(seed=42)
sim.add_layer("Lead", 5.0, 0.77, 0.58, 0.19, 11.34)

comparison = sim.compare_with_analytical(
    source_energy_MeV=1.0,
    num_photons=100_000
)

print(f"Monte Carlo: {comparison['mc_transmission']:.6f}")
print(f"Analytique:  {comparison['analytical_transmission']:.6f}")
print(f"Différence:  {comparison['difference_percent']:.2f}%")
print(f"Buildup:     {comparison['buildup_factor']:.2f}x")
```

## Résultats

L'objet `MonteCarloResult` contient :

- **`transmission_factor`** : Fraction de photons transmis (0 à 1)
- **`buildup_factor`** : Facteur de buildup de dose (≥ 1)
- **`dose_transmitted`** : Énergie moyenne transmise par photon (MeV)
- **`dose_absorbed`** : Énergie moyenne absorbée par photon (MeV)
- **`uncertainty`** : Incertitude statistique
- **`total_photons`** : Nombre total de photons simulés
- **`transmitted_photons`** : Nombre de photons transmis

## Conseils d'utilisation

### Nombre de photons

Plus il y a de photons, meilleure est la précision statistique :

```python
from shield_lite.core import estimate_required_photons

# Estimer le nombre de photons nécessaire pour 1% d'incertitude
n = estimate_required_photons(
    desired_uncertainty=0.01,    # 1%
    expected_transmission=0.1     # Estimation de la transmission
)
print(f"Photons recommandés: {n:,}")
```

**Recommandations** :
- Tests rapides : 10,000 photons
- Résultats précis : 100,000 - 500,000 photons
- Haute précision : 1,000,000+ photons

### Reproductibilité

Utilisez une seed fixe pour des résultats reproductibles :

```python
sim = MonteCarloShieldSimulator(seed=42)  # Résultats reproductibles
```

### Coefficients d'atténuation

Les coefficients dépendent de l'énergie du photon. Sources de données :

- **NIST XCOM** : https://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html
- **IAEA** : https://www-nds.iaea.org/

Pour 1 MeV dans le plomb :
- μ_total ≈ 0.77 cm⁻¹
- μ_Compton ≈ 0.58 cm⁻¹
- μ_photoélectrique ≈ 0.19 cm⁻¹

## Exemples complets

Lancer les exemples :

```bash
cd shield-lite
python examples/example_monte_carlo.py
```

Exemples inclus :
1. Blindage simple en plomb
2. Blindage multicouche (Pb + Béton + Acier)
3. Dépendance en énergie
4. Interface par dictionnaires

## Tests

```bash
cd shield-lite
pytest tests/test_monte_carlo.py -v
```

Tests inclus :
- Création du simulateur
- Ajout de couches
- Simulation simple
- Reproductibilité
- Décroissance de transmission avec épaisseur
- Facteur de buildup
- Interface par dictionnaires

## Architecture

```
shield-lite/
├── CMakeLists.txt                      # Configuration de compilation
├── pyproject.toml                      # Dépendances Python (+ pybind11)
├── src/shield_lite/
│   ├── cpp/                           # Code C++
│   │   ├── photon_transport.h        # Structures et classe de transport
│   │   ├── photon_transport.cpp      # Implémentation du transport
│   │   ├── monte_carlo.cpp           # Wrapper haut niveau
│   │   └── bindings.cpp              # Bindings pybind11
│   └── core/
│       └── monte_carlo.py            # Interface Python
├── examples/
│   └── example_monte_carlo.py        # Exemples d'utilisation
└── tests/
    └── test_monte_carlo.py           # Tests unitaires
```

## Physique implémentée

### Transport de photons

1. **Échantillonnage du libre parcours moyen** :
   ```
   λ = -ln(ξ) / μ_total
   ```

2. **Type d'interaction** :
   - Compton si ξ < μ_Compton / μ_total
   - Photoélectrique sinon

3. **Diffusion Compton** (formule de Klein-Nishina simplifiée) :
   ```
   E' = E / [1 + (E/m_e c²)(1 - cos θ)]
   ```

4. **Accumulation de dose** :
   - Dose transmise : énergie des photons sortants
   - Dose absorbée : énergie déposée dans le matériau

### Buildup factor

```
B = Dose_Monte_Carlo / Dose_Beer_Lambert
```

Le buildup factor représente l'augmentation de dose due aux photons diffusés. Il est toujours ≥ 1.

## Performance

Benchmarks typiques (processeur moderne, 1 thread) :

| Photons | Couches | Temps    |
|---------|---------|----------|
| 10,000  | 1       | ~10 ms   |
| 100,000 | 1       | ~100 ms  |
| 100,000 | 3       | ~150 ms  |
| 1,000,000| 1      | ~1 s     |

**Note** : La compilation avec `-O3 -march=native` (activée par défaut) optimise les performances.

## Limitations et extensions futures

### Limitations actuelles

1. **Géométrie 1D** : Transport uniquement dans la direction Z
2. **Diffusion isotrope** : Simplification de Klein-Nishina
3. **Coefficients constants** : μ devrait dépendre de l'énergie
4. **Pas de secondaires** : Électrons Compton non trackés

### Extensions possibles

1. **Géométrie 3D** : Transport dans toutes les directions
2. **Klein-Nishina complet** : Distribution angulaire réaliste
3. **Coefficients tabulés** : μ(E) depuis NIST
4. **Transport d'électrons** : Chaîne complète d'interactions
5. **Parallélisation** : OpenMP ou multithreading
6. **Géométries complexes** : Sphères, cylindres

## Troubleshooting

### Erreur de compilation

```
CMake Error: Could not find pybind11
```

**Solution** :
```bash
poetry install  # Installe pybind11
pip install pybind11[global]  # Alternative
```

### Import échoue

```python
ImportError: shield_lite._monte_carlo not found
```

**Solution** :
1. Vérifier que la compilation a réussi :
   ```bash
   ls build/_monte_carlo*.so  # Linux/macOS
   ls build/_monte_carlo*.pyd  # Windows
   ```

2. Copier le module compilé :
   ```bash
   cp build/_monte_carlo*.so src/shield_lite/
   ```

### Résultats bizarres

- **Vérifier les coefficients** : μ_total = μ_Compton + μ_photoélectrique
- **Augmenter le nombre de photons** : Plus de statistique
- **Vérifier l'énergie** : Les coefficients dépendent de E

## Contribuer

Pour étendre le module :

1. Modifier le code C++ dans `src/shield_lite/cpp/`
2. Recompiler : `cd build && make && cd ..`
3. Tester : `pytest tests/test_monte_carlo.py`
4. Documenter les changements

## Références

- **Klein-Nishina formula** : O. Klein, Y. Nishina, Z. Phys. 52, 853 (1929)
- **NIST XCOM** : M.J. Berger et al., NIST Standard Reference Database 8
- **Shielding theory** : J.E. Turner, "Atoms, Radiation, and Radiation Protection"

## Licence

MIT (comme le projet principal shield-lite)

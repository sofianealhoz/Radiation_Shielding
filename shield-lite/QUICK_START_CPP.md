# Quick Start - Monte Carlo C++

## Installation rapide (3 étapes)

### 1. Installer les dépendances

```bash
cd shield-lite
poetry install  # ou: pip install pybind11
```

### 2. Compiler le module C++

```bash
./build_cpp.sh
```

**Ou manuellement** :
```bash
mkdir -p build && cd build
cmake .. && make
cd ..
```

### 3. Tester

```bash
python3 examples/example_monte_carlo.py
```

## Utilisation basique

```python
from shield_lite.core import MonteCarloShieldSimulator

# Créer simulateur
sim = MonteCarloShieldSimulator(seed=42)

# Ajouter blindage (plomb 5 cm)
sim.add_layer("Lead", 5.0, 0.77, 0.58, 0.19, 11.34)

# Simuler 100k photons de 1 MeV
result = sim.run(source_energy_MeV=1.0, num_photons=100_000)

# Résultats
print(f"Transmission: {result.transmission_factor:.4f}")
print(f"Buildup: {result.buildup_factor:.2f}")
```

## Que fait ce module ?

**Simulation Monte Carlo** de transport de photons gamma :
- ✅ Simule les trajectoires individuelles de millions de photons
- ✅ Modélise la diffusion Compton et l'absorption photoélectrique
- ✅ Calcule le **buildup factor** (augmentation de dose due à la diffusion)
- ✅ ~100x plus rapide que Python grâce à C++

**Différence avec `dose()`** :
- `dose()` : Formule exponentielle simple (rapide, approximatif)
- Monte Carlo : Simulation physique réaliste (précis, tient compte de la diffusion)

## Exemples

Voir `examples/example_monte_carlo.py` pour :
1. Blindage simple (plomb)
2. Blindage multicouche (Pb + béton + acier)
3. Dépendance en énergie
4. Comparaison avec modèle analytique

## Documentation complète

Voir `CPP_MONTE_CARLO_README.md` pour :
- Détails physiques
- API complète
- Conseils d'utilisation
- Troubleshooting

## Structure des fichiers créés

```
shield-lite/
├── CMakeLists.txt                    # Configuration CMake
├── build_cpp.sh                      # Script de compilation
├── src/shield_lite/
│   ├── cpp/                         # Code C++
│   │   ├── photon_transport.h
│   │   ├── photon_transport.cpp
│   │   ├── monte_carlo.cpp
│   │   └── bindings.cpp
│   └── core/
│       └── monte_carlo.py           # Interface Python
├── examples/
│   └── example_monte_carlo.py       # Exemples
├── tests/
│   └── test_monte_carlo.py          # Tests
└── CPP_MONTE_CARLO_README.md        # Doc complète
```

## Problèmes ?

**Module ne compile pas ?**
```bash
# Vérifier dépendances
cmake --version
g++ --version
python3 -c "import pybind11"
```

**Import échoue ?**
```bash
# Vérifier fichier compilé
ls build/_monte_carlo*.so

# Copier manuellement si nécessaire
cp build/_monte_carlo*.so src/shield_lite/
```

**Recompiler depuis zéro ?**
```bash
./build_cpp.sh clean
```

---

**Questions ?** Lire `CPP_MONTE_CARLO_README.md`

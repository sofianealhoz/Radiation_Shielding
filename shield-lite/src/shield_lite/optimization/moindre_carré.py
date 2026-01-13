import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

def fit_S(y: np.ndarray) -> dict:
    def model(x, a, b):
        return a * x + b

    x_data = np.arange(len(y))
    params, _ = curve_fit(model, x_data, y)
    return {'S': params[0], 'intercept': params[1]}


def fit_S_mu_eff(t: np.ndarray, y: np.ndarray) -> dict:
    def model(x, mu_eff):
        return np.exp(-mu_eff * x)

    params, _ = curve_fit(model, t, y)
    return {'mu_eff': params[0]}

def fit_from_csv(filepath: str, t_col: str = 'thickness_mm', y_col: str = 'dose') -> dict:
    """
    Charge des données expérimentales depuis un CSV et ajuste le modèle physique.
    Modèle : y = S * exp(-mu * (t / 10))  (conversion mm -> cm pour mu en cm^-1)
    """
    # 1. Chargement des données
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier {filepath} est introuvable.")
    
    if t_col not in df.columns or y_col not in df.columns:
        raise ValueError(f"Les colonnes '{t_col}' et '{y_col}' doivent exister dans le CSV.")

    t_data = df[t_col].values
    y_data = df[y_col].values

    # 2. Définition du modèle physique
    # On divise t par 10 car t est en mm et on veut mu en cm^-1
    def physical_model(t_mm, S, mu):
        return S * np.exp(-mu * (t_mm / 10.0))

    # 3. Estimation initiale (Guess) pour aider l'algorithme
    # S ~ max(y) (dose sans écran)
    # mu ~ 0.1 (valeur typique)
    initial_guess = [np.max(y_data), 0.1]

    # 4. Optimisation (Moindres Carrés Non-Linéaires)
    try:
        popt, pcov = curve_fit(physical_model, t_data, y_data, p0=initial_guess)
    except RuntimeError:
        raise RuntimeError("La calibration a échoué (les données ne suivent pas une loi exponentielle ?)")

    S_hat, mu_hat = popt

    # 5. Calcul des métriques de qualité
    y_pred = physical_model(t_data, S_hat, mu_hat)
    residuals = y_data - y_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_data - np.mean(y_data))**2)
    
    # Protection contre la division par zéro si y est constant
    if ss_tot == 0:
        r_squared = 0.0
    else:
        r_squared = 1 - (ss_res / ss_tot)
        
    rmse = np.sqrt(np.mean(residuals**2))

    return {
        "S_hat": S_hat,       # Intensité estimée de la source
        "mu_hat": mu_hat,     # Coefficient d'atténuation estimé (cm^-1)
        "R2": r_squared,      # Qualité du fit (proche de 1.0 = parfait)
        "RMSE": rmse,         # Erreur moyenne
        "covariance": pcov.tolist() # Pour calculer les incertitudes si besoin
    }
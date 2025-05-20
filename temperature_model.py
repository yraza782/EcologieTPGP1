from scipy.integrate import odeint
import numpy as np

# --- Version avec Scipy odeint (modèle scientifique) ---
def temperature_derivative(Tc, t, Ta, I, ws):
    """
    Dérivée de Tc pour utilisation avec scipy.odeint.
    Utilisée pour la méthode de résolution mathématique classique.
    """
    dTc_dt = -((ws**2) / 1600) * 0.4 - 0.1 * (Tc - Ta) - ((I**1.4) / 73785) * 130
    return dTc_dt

# --- Dérivée manuelle de la température (modèle réaliste adapté) ---
def dTc_dt(Tc, Ta, I, ws):
    """
    Calcule la dérivée de la température Tc en fonction du temps,
    selon la formule issue du sujet + facteur de lissage réaliste.
    """
    facteur_refroidissement = ((-ws**2) / 1600) * 0.4 - 0.01
    terme_chauffage = (Tc - Ta - ((I**1.4) / 73785) * 130)
    return (1 / 60) * facteur_refroidissement * terme_chauffage

# --- Simulation minute par minute avec boucle for ---
def predict_temperature_manual(Tc0, Ta, I, ws, duration_min=30):
    """
    Simulation minute par minute en utilisant une boucle for externe.
    Chaque minute est simulée avec une intégration en pas de 0.001s.
    Retourne une température prédites à la fin de chaque minute.
    """
    dt = 0.001  # pas de temps en seconde
    steps_per_minute = int(60 / dt)  # nombre de pas pour une minute
    Tc = Tc0
    resultats = []

    for _ in range(duration_min):
        for _ in range(steps_per_minute):
            Tc += dTc_dt(Tc, Ta, I, ws) * dt
        resultats.append(round(Tc, 2))  # enregistrer la température à la fin de chaque minute

    return resultats

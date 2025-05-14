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

# --- Version odeint désactivée pour l’instant ---
# def predict_temperature(Tc0, Ta, I, ws, duration_min=30):
#     """
#     Simulation avec scipy.odeint (méthode scientifique).
#     Retourne une valeur par minute.
#     """
#     t = np.linspace(0, duration_min * 60, duration_min * 60)
#     Tc_values = odeint(temperature_derivative, Tc0, t, args=(Ta, I, ws))
#     Tc_per_min = Tc_values[::60].flatten().tolist()
#     return Tc_per_min

# --- Dérivée manuelle de la température (modèle réaliste adapté) ---
def dTc_dt(Tc, Ta, I, ws):
    """
    Calcule la dérivée de la température Tc en fonction du temps,
    selon la formule issue du sujet + facteur de lissage réaliste.
    """
    facteur_refroidissement = ((-ws**2) / 1600) * 0.4 - 0.01  # Réduction du facteur thermique (était -0.1)
    terme_chauffage = (Tc - Ta - ((I**1.4) / 73785) * 130)
    return (1 / 60) * facteur_refroidissement * terme_chauffage

# --- Simulation manuelle avec boucle (Euler) ---
def predict_temperature_manual(Tc0, Ta, I, ws, duration_min=30):
    dt = 0.001  # pas de temps en seconde (~10 millisecondes)
    total_time = duration_min * 60  # temps total en secondes
    steps = int(total_time / dt)

    Tc = Tc0
    resultats = []
    minute_mark = 0

    for i in range(steps):
        Tc += dTc_dt(Tc, Ta, I, ws) * dt

        # Enregistrer 1 valeur par minute
        if i * dt >= minute_mark * 60:
            resultats.append(round(Tc, 2))
            minute_mark += 1
            if minute_mark > duration_min:
                break

    return resultats

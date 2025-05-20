from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import matplotlib.pyplot as plt
import uuid
import os
import numpy as np
from codecarbon import EmissionsTracker
from scipy.integrate import odeint


# --- Initialisation FastAPI ---
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Modèles API ---
class SimulationInput(BaseModel):
    Tc: float
    Ta: float
    I: float
    ws: float

class SimulationOutput(BaseModel):
    minutes: List[int]
    Tc_values: List[float]

# --- Calcul de variation de température ---
def dTc_dt(Tc, t, Ta, I, ws):
    facteur = ((-ws**2 / 1600) * 0.4 - 0.1)
    partie_chauffage = (Tc - Ta - (I**1.4 / 73785) * 130)
    return (1/60) * facteur * partie_chauffage

# --- Simulation complète sur 30 min ---
def simulate(Tc, Ta, I, ws):
    total_time_sec = 30 * 60  # 30 minutes
    dt = 1e-4  # 1 ms
    t = np.arange(0, total_time_sec, dt)

    # Résolution de l'équation différentielle avec odeint
    Tc_result = odeint(dTc_dt, Tc, t, args=(Ta, I, ws)).flatten()

    # Prendre 1 point toutes les 60000 itérations (60 sec / 0.001)
    indices_minutes = np.arange(0, len(t), int(60 / dt))
    Tc_minutes = [round(Tc_result[i], 2) for i in indices_minutes]
    minutes = list(range(len(Tc_minutes)))

    return minutes, Tc_minutes

# --- API JSON (optionnelle) ---
@app.post("/simulate", response_model=SimulationOutput)
def simulate_temperature(data: SimulationInput):
    temps, valeurs = simulate(data.Tc, data.Ta, data.I, data.ws)
    return {"minutes": temps, "Tc_values": valeurs}

# --- Formulaire HTML ---
@app.get("/", response_class=HTMLResponse)
def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
def form_post(
    request: Request,
    Tc: float = Form(...),
    Ta: float = Form(...),
    I: float = Form(...),
    ws: float = Form(...)
):
    
    try:
        # 📉 Démarrage suivi carbone
        tracker = EmissionsTracker(output_dir="static", measure_power_secs=1)
        tracker.start()

        # 🔢 Simulation d’un calcul énergivore
        _ = np.random.random((10000, 10000))

        # 🔥 Simulation de température avec odeint
        temps, valeurs = simulate(Tc, Ta, I, ws)

        # 📈 Génération du graphique
        filename = f"{uuid.uuid4().hex}.png"
        filepath = f"static/{filename}"
        plt.figure()
        plt.plot(temps, valeurs, marker='o')
        plt.xlabel("Temps (minutes)")
        plt.ylabel("Température Tc (°C)")
        plt.title("Évolution de Tc")
        plt.grid(True)
        plt.savefig(filepath)
        plt.close()

        # 🧾 Fin du suivi carbone
        emissions = tracker.stop()
        data = tracker.final_emissions_data
        energy_kwh = data.energy_consumed

        return templates.TemplateResponse("form.html", {
            "request": request,
            "image_path": f"/static/{filename}",
            "emissions": f"{emissions:.6f} kgCO2eq",
            "energy": f"{energy_kwh:.6f} kWh"
        })

    except Exception as e:
        print("❌ ERREUR SERVEUR :", e)
        return HTMLResponse(content=f"<h1>Erreur : {e}</h1>", status_code=500)

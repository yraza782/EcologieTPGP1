from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import matplotlib.pyplot as plt
import uuid
import numpy as np
from codecarbon import EmissionsTracker
from numba import jit

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

# --- Fonction dérivée optimisée ---
@jit(nopython=True)
def dTc_dt(Tc, t, Ta, I, ws):
    facteur = ((-ws**2 / 1600) * 0.4 - 0.1)
    partie_chauffage = (Tc - Ta - (I**1.4 / 73785) * 130)
    return (1/60) * facteur * partie_chauffage

# --- Simulation optimisée via Euler ---
@jit(nopython=True)
def simulate_jit(Tc0, Ta, I, ws, total_minutes=30):
    dt = 0.001  # 1 ms
    steps = int((total_minutes * 60) / dt)
    Tc_vals = np.zeros(steps)
    Tc_vals[0] = Tc0

    for i in range(1, steps):
        Tc_vals[i] = Tc_vals[i-1] + dt * dTc_dt(Tc_vals[i-1], i*dt, Ta, I, ws)

    indices = np.arange(0, steps, int(60 / dt))
    Tc_minutes = np.round(Tc_vals[indices], 2)
    minutes = np.arange(len(Tc_minutes))

    return minutes, Tc_minutes

# --- API JSON ---
@app.post("/simulate", response_model=SimulationOutput)
def simulate_temperature(data: SimulationInput):
    minutes_np, Tc_np = simulate_jit(data.Tc, data.Ta, data.I, data.ws)
    return {
        "minutes": minutes_np.tolist(),
        "Tc_values": Tc_np.tolist()
    }

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
        # 📉 Suivi carbone
        tracker = EmissionsTracker(output_dir="static", measure_power_secs=1)
        tracker.start()

        # 🔢 Simulation énergivore (dummy charge)
        _ = np.random.random((10000, 10000))

        # 🔥 Simulation température
        minutes_np, Tc_np = simulate_jit(Tc, Ta, I, ws)
        temps, valeurs = minutes_np.tolist(), Tc_np.tolist()

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

        # 🧾 Fin suivi carbone
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

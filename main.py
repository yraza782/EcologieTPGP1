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

# ✅ Import de la version compilée Cython
from simulate_core import simulate as simulate_cython

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

# --- Wrapper pour appel Cython ---
def simulate(Tc, Ta, I, ws):
    return simulate_cython(Tc, Ta, I, ws)

# --- API JSON ---
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
        # 📉 Suivi carbone
        tracker = EmissionsTracker(output_dir="static", measure_power_secs=1)
        tracker.start()

        # 🔢 Simulation énergivore (dummy charge)
        _ = np.random.random((10000, 10000))

        # 🔥 Simulation température avec Cython
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

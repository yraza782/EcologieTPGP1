from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from codecarbon import EmissionsTracker
from temperature_model import predict_temperature_manual
import numpy as np

# --- Initialisation FastAPI ---
app = FastAPI()

# --- CORS pour permettre les appels JS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ à restreindre si nécessaire
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Templates HTML (pour servir index.html) ---
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Modèle de données reçu ---
class InputData(BaseModel):
    Tc0: float
    Ta: float
    I: float
    ws: float

# --- Route API POST ---
@app.post("/predict")
def predict(data: InputData):
    from codecarbon import EmissionsTracker
    import numpy as np

    # Démarrer le suivi d'émissions
    tracker = EmissionsTracker()
    tracker.start()

    # Charger le CPU pour déclencher une empreinte mesurable
    for _ in range(5):
        _ = np.random.random((10000, 10000))

    # Simulation thermique
    resultats = predict_temperature_manual(data.Tc0, data.Ta, data.I, data.ws)

    # Arrêter le suivi et récupérer les données
    tracker.stop()
    details = tracker.final_emissions_data


    return {
        "input": data.dict(),
        "temperature_prevue": resultats,
        "emissions_kgCO2": round(details.emissions, 6),
        "energy_consumed_kWh": round(details.energy_consumed, 6)
    }

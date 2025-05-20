import requests
import random
import time
from codecarbon import EmissionsTracker

# URL de l'API
url = "http://localhost:8000/predict"

# Paramétrage test
nb_users = 1000  # ← modifie ici pour tester 10, 100 ou 1000
duration = 60    # en secondes

# Suivi énergétique
tracker = EmissionsTracker(project_name=f"{nb_users}_users_test")
tracker.start()

start = time.time()

for i in range(nb_users):
    payload = {
        "Tc0": 25.0,
        "Ta": 20.0 + random.uniform(-3, 3),
        "I": random.uniform(10, 100),
        "ws": random.uniform(0.5, 8)
    }
    try:
        r = requests.post(url, json=payload)
        print(f"[{i}] Status: {r.status_code}")
    except Exception as e:
        print(f"[{i}] Échec : {e}")
    
    # Répartir les requêtes uniformément sur 1 minute
    time.sleep(duration / nb_users)

tracker.stop()
print("Test terminé.")

# simulate_core.pyx
import numpy as np
cimport numpy as np
from libc.math cimport pow

def dTc_dt(double Tc, double t, double Ta, double I, double ws):
    cdef double facteur = ((-ws * ws / 1600) * 0.4 - 0.1)
    cdef double partie_chauffage = Tc - Ta - pow(I, 1.4) * 130.0 / 73785.0
    return (1.0 / 60.0) * facteur * partie_chauffage

def simulate(double Tc0, double Ta, double I, double ws, int minutes=30):
    cdef double dt = 0.001  # 1 ms
    cdef int steps = int((minutes * 60) / dt)
    cdef np.ndarray[np.float64_t, ndim=1] Tc_vals = np.zeros(steps, dtype=np.float64)
    cdef np.ndarray[np.float64_t, ndim=1] times = np.zeros(steps, dtype=np.float64)
    Tc_vals[0] = Tc0

    cdef int i
    for i in range(1, steps):
        times[i] = i * dt
        Tc_vals[i] = Tc_vals[i-1] + dt * dTc_dt(Tc_vals[i-1], times[i], Ta, I, ws)

    cdef int n_minutes = minutes
    cdef np.ndarray[np.float64_t, ndim=1] Tc_per_min = np.zeros(n_minutes, dtype=np.float64)
    cdef np.ndarray[np.int32_t, ndim=1] min_indices = np.arange(0, steps, int(60 / dt), dtype=np.int32)

    for i in range(n_minutes):
        Tc_per_min[i] = round(Tc_vals[min_indices[i]], 2)

    return min_indices.tolist(), Tc_per_min.tolist()

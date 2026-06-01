from __future__ import annotations

import numpy as np
from scipy import stats

DIST_MAP = {
    "Gumbel_Momentos": "gumbel_r",
    "Gumbel_MLE": "gumbel_r",
    "Exponencial_1P": "expon",
    "Exponencial_2P": "expon",
    "GEV_MLE": "genextreme",
}


def scipy_dist(nombre: str):
    key = DIST_MAP.get(nombre)
    if key == "gumbel_r":
        return stats.gumbel_r
    if key == "expon":
        return stats.expon
    if key == "genextreme":
        return stats.genextreme
    raise ValueError(f"Distribucin no mapeada: {nombre}")


def params_desde_fila(distribucion: str, row) -> tuple:
    if distribucion == "Gumbel_Momentos":
        return (float(row["param_1"]), float(row["param_2"]))
    if distribucion == "Gumbel_MLE":
        return (float(row["param_1"]), float(row["param_2"]))
    if distribucion == "Exponencial_1P":
        return (0.0, float(row["param_2"]))
    if distribucion == "Exponencial_2P":
        return (float(row["param_1"]), float(row["param_3"]))
    if distribucion == "GEV_MLE":
        return (float(row["param_1"]), float(row["param_2"]), float(row["param_3"]))
    raise ValueError(distribucion)


def cuantiles_teoricos(datos: np.ndarray, distribucion: str, params: tuple) -> np.ndarray:
    datos = np.sort(np.asarray(datos, dtype=float))
    n = len(datos)
    p_emp = np.arange(1, n + 1) / (n + 1)
    dist = scipy_dist(distribucion)
    return dist.ppf(p_emp, *params)

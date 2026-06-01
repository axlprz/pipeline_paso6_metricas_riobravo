from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .ajuste_distribuciones import cuantiles_teoricos, params_desde_fila, scipy_dist


def mae_bias_rmse_cuantiles(datos: np.ndarray, q_teo: np.ndarray) -> dict[str, float]:
    resid = datos - q_teo
    return {
        "MAE": float(np.mean(np.abs(resid))),
        "Sesgo": float(np.mean(resid)),
        "RMSE_cuantiles": float(np.sqrt(np.mean(resid**2))),
    }


def anderson_darling(datos: np.ndarray, distribucion: str, params: tuple) -> float:
    """Estadístico A² de Anderson-Darling con CDF teórica."""
    datos = np.sort(np.asarray(datos, dtype=float))
    n = len(datos)
    dist = scipy_dist(distribucion)
    f = np.clip(dist.cdf(datos, *params), 1e-10, 1 - 1e-10)
    i = np.arange(1, n + 1)
    s = (2 * i - 1) * (np.log(f) + np.log(1 - f[::-1]))
    return float(-n - np.sum(s) / n)


def chi_cuadrado_binned(
    datos: np.ndarray, distribucion: str, params: tuple, n_bins: int = 8
) -> tuple[float, float]:
    datos = np.sort(np.asarray(datos, dtype=float))
    dist = scipy_dist(distribucion)
    edges = np.quantile(datos, np.linspace(0, 1, n_bins + 1))
    edges = np.unique(edges)
    if len(edges) < 3:
        return np.nan, np.nan
    obs, _ = np.histogram(datos, bins=edges)
    cdf_edges = dist.cdf(edges, *params)
    prob = np.diff(cdf_edges)
    prob = np.maximum(prob, 1e-12)
    exp = prob * len(datos)
    exp = np.maximum(exp, 1.0)
    chi2 = float(np.sum((obs - exp) ** 2 / exp))
    dof = max(len(obs) - 1 - len(params), 1)
    pvalue = float(1 - stats.chi2.cdf(chi2, dof))
    return chi2, pvalue


def ampliar_metricas(
    datos_por_rio: dict[str, np.ndarray],
    parametros: pd.DataFrame,
    bondad: pd.DataFrame,
) -> pd.DataFrame:
    filas = []
    for _, row in bondad.iterrows():
        rio = row["Rio"]
        dist = row["Distribucion"]
        datos = np.asarray(datos_por_rio[rio], dtype=float)
        prow = parametros[
            (parametros["Rio"] == rio) & (parametros["Distribucion"] == dist)
        ]
        if prow.empty:
            continue
        params = params_desde_fila(dist, prow.iloc[0])
        q_teo = cuantiles_teoricos(datos, dist, params)
        extra = mae_bias_rmse_cuantiles(datos, q_teo)
        try:
            ad = anderson_darling(datos, dist, params)
        except Exception:
            ad = np.nan
        try:
            chi2, chi2_p = chi_cuadrado_binned(datos, dist, params)
        except Exception:
            chi2, chi2_p = np.nan, np.nan
        filas.append(
            {
                **row.to_dict(),
                **extra,
                "AD_stat": ad,
                "Chi2_stat": chi2,
                "Chi2_pvalue": chi2_p,
            }
        )
    return pd.DataFrame(filas)

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .ajuste_distribuciones import cuantiles_teoricos, params_desde_fila, scipy_dist


def qq_plot(datos: np.ndarray, distribucion: str, params: tuple, out_path: Path, titulo: str):
    datos = np.sort(np.asarray(datos, dtype=float))
    n = len(datos)
    p = np.arange(1, n + 1) / (n + 1)
    dist = scipy_dist(distribucion)
    q_teo = dist.ppf(p, *params)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(q_teo, datos, s=18, alpha=0.75)
    lim = [min(q_teo.min(), datos.min()), max(q_teo.max(), datos.max())]
    ax.plot(lim, lim, "k--", lw=1)
    ax.set_xlabel("Cuantiles teóricos")
    ax.set_ylabel("Cuantiles observados")
    ax.set_title(titulo)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def cdf_empirica_vs_teorica(
    datos: np.ndarray, distribucion: str, params: tuple, out_path: Path, titulo: str
):
    datos = np.sort(np.asarray(datos, dtype=float))
    n = len(datos)
    f_emp = np.arange(1, n + 1) / (n + 1)
    dist = scipy_dist(distribucion)
    f_teo = dist.cdf(datos, *params)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(datos, f_emp, "o", ms=3, label="Empírica (Weibull)")
    ax.plot(datos, f_teo, "-", lw=1.5, label="Teórica")
    ax.set_xlabel("Máximo anual")
    ax.set_ylabel("Probabilidad acumulada")
    ax.set_title(titulo)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def curva_periodo_retorno(
    periodos: list[int], q_vals: list[float], out_path: Path, titulo: str
):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(periodos, q_vals, "o-")
    ax.set_xscale("log")
    ax.set_xlabel("Periodo de retorno T (años)")
    ax.set_ylabel("Caudal / entrega Q_T")
    ax.set_title(titulo)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def generar_graficas_rio(
    rio: str,
    datos: np.ndarray,
    parametros: pd.DataFrame,
    retornos: pd.DataFrame,
    periodos: list[int],
    out_dir: Path,
):
    sub = out_dir / rio.replace(" ", "_")
    sub.mkdir(parents=True, exist_ok=True)
    for _, row in parametros[parametros["Rio"] == rio].iterrows():
        dist = row["Distribucion"]
        params = params_desde_fila(dist, row)
        titulo = f"{rio} — {dist}"
        qq_plot(datos, dist, params, sub / f"qq_{dist}.png", titulo)
        cdf_empirica_vs_teorica(
            datos, dist, params, sub / f"cdf_{dist}.png", titulo
        )
    mejor = retornos[retornos["Rio"] == rio].iloc[0]
    cols = [f"Q_T_{t}" for t in periodos]
    q = [mejor[c] for c in cols]
    curva_periodo_retorno(
        periodos,
        q,
        sub / f"retornos_{mejor['Distribucion']}.png",
        f"{rio} — {mejor['Distribucion']} (mejor AIC notebook)",
    )

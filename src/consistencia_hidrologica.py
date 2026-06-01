from __future__ import annotations

import numpy as np
import pandas as pd


def verificar_monotonia_retornos(
    df: pd.DataFrame, periodos: list[int], tol: float = 1e-6
) -> pd.DataFrame:
    cols = [f"Q_T_{t}" for t in periodos]
    filas = []
    for _, row in df.iterrows():
        vals = [row[c] for c in cols if c in row and pd.notna(row[c])]
        ok = all(vals[i] + tol <= vals[i + 1] for i in range(len(vals) - 1))
        filas.append(
            {
                "Rio": row["Rio"],
                "Distribucion": row["Distribucion"],
                "monotonia_Q_T": ok,
            }
        )
    return pd.DataFrame(filas)


def comparar_con_maximo_historico(
    df_retornos: pd.DataFrame,
    max_historico: dict[str, float],
    periodos: list[int],
    ratio_alerta: float,
) -> pd.DataFrame:
    q_col = f"Q_T_{max(periodos)}"
    filas = []
    for _, row in df_retornos.iterrows():
        rio = row["Rio"]
        q100 = row.get(q_col, np.nan)
        mx = max_historico.get(rio, np.nan)
        ratio = q100 / mx if mx and mx > 0 else np.nan
        filas.append(
            {
                "Rio": rio,
                "Distribucion": row["Distribucion"],
                "maximo_historico": mx,
                q_col: q100,
                "ratio_Q100_vs_max": ratio,
                "alerta_extrapolacion": bool(ratio > ratio_alerta) if pd.notna(ratio) else False,
                "Q100_menor_que_max": bool(q100 < mx) if pd.notna(q100) and pd.notna(mx) else False,
            }
        )
    return pd.DataFrame(filas)


def checklist_consistencia(
    monotonia: pd.DataFrame,
    extrapolacion: pd.DataFrame,
    conflictos: pd.DataFrame,
) -> pd.DataFrame:
    base = monotonia.merge(extrapolacion, on=["Rio", "Distribucion"])
    chk = base.merge(conflictos, on="Rio", how="left")
    chk["apto_hidrologico"] = (
        chk["monotonia_Q_T"]
        & ~chk["alerta_extrapolacion"]
        & ~chk.get("conflicto_metricas", False)
    )
    return chk

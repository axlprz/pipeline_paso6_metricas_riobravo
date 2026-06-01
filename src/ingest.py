from __future__ import annotations

from pathlib import Path

import pandas as pd

ARCHIVOS_NOTEBOOK = {
    "maximos_anuales": "01_maximos_anuales.csv",
    "validacion": "02_validacion.csv",
    "resumen_descriptivo": "03_resumen_descriptivo.csv",
    "parametros": "04_parametros_estimados.csv",
    "bondad_ajuste": "05_bondad_ajuste.csv",
    "periodos_retorno": "06_periodos_retorno.csv",
    "mejor_aic": "07_tabla_final_mejor_aic.csv",
}


def cargar_resultados_notebook(resultados_dir: Path) -> dict[str, pd.DataFrame]:
    if not resultados_dir.is_dir():
        raise FileNotFoundError(f"No existe carpeta de resultados: {resultados_dir}")
    out: dict[str, pd.DataFrame] = {}
    for nombre, archivo in ARCHIVOS_NOTEBOOK.items():
        path = resultados_dir / archivo
        if not path.exists():
            raise FileNotFoundError(f"Falta entregable del notebook (pasos 2–5): {path}")
        out[nombre] = pd.read_csv(path)
    return out


def cargar_resultados_distribuciones(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def maximos_por_rio(df_max: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        rio: grupo.sort_values("Anio")["Maximo_Anual"].reset_index(drop=True)
        for rio, grupo in df_max.groupby("Rio")
    }


def fusionar_bondad_y_retornos(bondad: pd.DataFrame, retornos: pd.DataFrame) -> pd.DataFrame:
    cols_ret = [c for c in retornos.columns if c.startswith("Q_T_")]
    base = ["Rio", "Distribucion"]
    return bondad.merge(retornos[base + cols_ret], on=base, how="left")

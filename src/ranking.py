from __future__ import annotations

import pandas as pd


def _rank_norm(series: pd.Series, ascending: bool = True) -> pd.Series:
    r = series.rank(ascending=ascending, method="average")
    if r.max() > r.min():
        return (r - r.min()) / (r.max() - r.min())
    return pd.Series(0.5, index=series.index)


def ranking_por_rio(df: pd.DataFrame, pesos: dict[str, float]) -> pd.DataFrame:
    out = []
    for rio, grupo in df.groupby("Rio"):
        g = grupo.copy()
        score = 0.0
        for metrica, peso in pesos.items():
            if metrica not in g.columns:
                continue
            asc = metrica != "KS_pvalue"
            if metrica == "KS_pvalue":
                norm = _rank_norm(g[metrica], ascending=False)
            else:
                norm = _rank_norm(g[metrica], ascending=asc)
            score = score + peso * norm
        g["score_compuesto"] = score
        g["ranking_global"] = g["score_compuesto"].rank(ascending=True, method="dense").astype(int)
        g["ranking_AIC"] = g["AIC"].rank(ascending=True, method="dense").astype(int)
        g["ranking_KS"] = g["KS_stat"].rank(ascending=True, method="dense").astype(int)
        g["ranking_RMSE"] = g["RMSE_prob"].rank(ascending=True, method="dense").astype(int)
        if "AD_stat" in g.columns:
            g["ranking_AD"] = g["AD_stat"].rank(ascending=True, method="dense").astype(int)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def mejor_por_criterio(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    asc = columna not in ("KS_pvalue",)
    return (
        df.sort_values(["Rio", columna], ascending=[True, asc])
        .groupby("Rio", as_index=False)
        .first()
    )


def conflictos_entre_metricas(df_rank: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for rio, g in df_rank.groupby("Rio"):
        mejor_aic = g.loc[g["ranking_AIC"] == 1, "Distribucion"].iloc[0]
        mejor_ks = g.loc[g["ranking_KS"] == 1, "Distribucion"].iloc[0]
        mejor_rmse = g.loc[g["ranking_RMSE"] == 1, "Distribucion"].iloc[0]
        conflicto = len({mejor_aic, mejor_ks, mejor_rmse}) > 1
        filas.append(
            {
                "Rio": rio,
                "mejor_AIC": mejor_aic,
                "mejor_KS": mejor_ks,
                "mejor_RMSE": mejor_rmse,
                "conflicto_metricas": conflicto,
            }
        )
    return pd.DataFrame(filas)

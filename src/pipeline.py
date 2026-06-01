from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from .config import PIPELINE_ROOT, load_config, resolve_path, salida_dir
from .consistencia_hidrologica import (
    checklist_consistencia,
    comparar_con_maximo_historico,
    verificar_monotonia_retornos,
)
from .ingest import (
    cargar_resultados_distribuciones,
    cargar_resultados_notebook,
    fusionar_bondad_y_retornos,
    maximos_por_rio,
)
from .metricas import ampliar_metricas
from .ranking import conflictos_entre_metricas, mejor_por_criterio, ranking_por_rio
from .visualizacion import generar_graficas_rio


def _maximos_historicos(df_max: pd.DataFrame) -> dict[str, float]:
    return df_max.groupby("Rio")["Maximo_Anual"].max().to_dict()


def ejecutar_fase1(cfg: dict) -> dict:
    """Framework de evaluación: criterios, métricas y checklist (antes de todos los resultados)."""
    out = salida_dir(cfg, "fase1")
    catalogo = pd.DataFrame(
        [
            {"categoria": "Error", "metrica": "RMSE_prob", "descripcion": "RMSE entre F empírica (Weibull) y F teórica"},
            {"categoria": "Error", "metrica": "MAE", "descripcion": "Error absoluto medio en cuantiles de probabilidad"},
            {"categoria": "Error", "metrica": "Sesgo", "descripcion": "Sesgo medio en cuantiles"},
            {"categoria": "Ajuste", "metrica": "logLik", "descripcion": "Log-verosimilitud"},
            {"categoria": "Ajuste", "metrica": "AIC", "descripcion": "Criterio de información de Akaike"},
            {"categoria": "Ajuste", "metrica": "BIC", "descripcion": "Criterio bayesiano de Schwarz"},
            {"categoria": "Prueba", "metrica": "KS_stat", "descripcion": "Kolmogorov-Smirnov (menor es mejor)"},
            {"categoria": "Prueba", "metrica": "KS_pvalue", "descripcion": "p-valor KS (>0.05 no rechaza)"},
            {"categoria": "Prueba", "metrica": "AD_stat", "descripcion": "Anderson-Darling (menor es mejor)"},
            {"categoria": "Prueba", "metrica": "Chi2_stat", "descripcion": "Chi-cuadrado en bins (menor es mejor)"},
        ]
    )
    catalogo.to_csv(out / "01_catalogo_metricas.csv", index=False)

    criterios = pd.DataFrame(
        [
            {"criterio": "ranking_AIC", "regla": "Menor AIC ? mejor balance ajuste/complejidad"},
            {"criterio": "ranking_KS", "regla": "Menor KS_stat; complementar con KS_pvalue ? alpha"},
            {"criterio": "ranking_RMSE", "regla": "Menor RMSE en probabilidades"},
            {"criterio": "score_compuesto", "regla": "Promedio ponderado normalizado (ver config.yaml)"},
            {"criterio": "consistencia_hidrologica", "regla": "Monotonía Q_T, ratio Q100 vs máximo histórico, sin conflictos fuertes"},
        ]
    )
    criterios.to_csv(out / "02_criterios_seleccion.csv", index=False)

    checklist = pd.DataFrame(
        [
            {"id": "H1", "verificacion": "Monotonía Q_T_2 < … < Q_T_100", "obligatorio": True},
            {"id": "H2", "verificacion": "Q_T_100 no excede ratio configurable vs máximo observado", "obligatorio": True},
            {"id": "H3", "verificacion": "Cola de distribución coherente con eventos históricos", "obligatorio": True},
            {"id": "H4", "verificacion": "Concordancia entre mejor AIC y mejor KS/RMSE", "obligatorio": False},
        ]
    )
    checklist.to_csv(out / "03_checklist_consistencia_hidrologica.csv", index=False)

    mapa_pasos = pd.DataFrame(
        [
            {"paso": 1, "tema": "Introducción", "responsables": "Fernando, Alfonso", "insumo_pipeline": "Contexto (PDF introducción)"},
            {"paso": 2, "tema": "Base de datos y QC", "responsables": "Fernando", "insumo_pipeline": "02_validacion.csv"},
            {"paso": 3, "tema": "Series de frecuencias", "responsables": "Cecilia Téllez, Carlos Franco", "insumo_pipeline": "01_maximos_anuales.csv"},
            {"paso": 4, "tema": "Distribuciones a comparar", "responsables": "Ana Rosa, Kay, Cecy, Carlos", "insumo_pipeline": "Probabilística.pdf + CSV fase2"},
            {"paso": 5, "tema": "Estimación de parámetros", "responsables": "Luis Fernando", "insumo_pipeline": "04_parametros_estimados.csv"},
            {"paso": 6, "tema": "Métricas y bondad de ajuste", "responsables": "Axel", "insumo_pipeline": "Este pipeline (fases 1 y 2)"},
            {"paso": 7, "tema": "Periodos de retorno", "responsables": "Diego Pallares, Braulio", "insumo_pipeline": "06_periodos_retorno.csv"},
        ]
    )
    mapa_pasos.to_csv(out / "04_mapa_integracion_pasos_1_5.csv", index=False)

    brecha = pd.DataFrame(
        {
            "fuente": ["Notebook (paso 5)", "Documento Probabilística (paso 4)"],
            "n_distribuciones": [
                len(cfg["distribuciones_notebook"]),
                len(cfg["distribuciones_documento"]),
            ],
            "distribuciones": [
                ", ".join(cfg["distribuciones_notebook"]),
                ", ".join(cfg["distribuciones_documento"]),
            ],
        }
    )
    brecha.to_csv(out / "05_brecha_distribuciones_paso4_vs_5.csv", index=False)

    meta = {
        "fase": 1,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "mensaje": "Framework listo. Ejecutar fase 2 cuando existan CSV unificados.",
    }
    (out / "manifest_fase1.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def ejecutar_fase2(cfg: dict) -> dict:
    """Aplicación de métricas sobre resultados recibidos (notebook + opcional equipo paso 4)."""
    out = salida_dir(cfg, "fase2")
    graf_dir = out / "graficas"
    graf_dir.mkdir(exist_ok=True)

    res_dir = resolve_path(cfg, "notebook_resultados")
    datos_nb = cargar_resultados_notebook(res_dir)
    series = {k: v.values for k, v in maximos_por_rio(datos_nb["maximos_anuales"]).items()}
    max_hist = _maximos_historicos(datos_nb["maximos_anuales"])

    ampliada = ampliar_metricas(series, datos_nb["parametros"], datos_nb["bondad_ajuste"])
    ampliada.to_csv(out / "01_metricas_ampliadas_notebook.csv", index=False)

    rank = ranking_por_rio(ampliada, cfg["criterios"]["pesos_ranking"])
    rank.to_csv(out / "02_ranking_modelos.csv", index=False)

    conflictos = conflictos_entre_metricas(rank)
    conflictos.to_csv(out / "03_conflictos_entre_metricas.csv", index=False)

    fusion = fusionar_bondad_y_retornos(ampliada, datos_nb["periodos_retorno"])
    fusion.to_csv(out / "04_tabla_comparativa_completa.csv", index=False)

    mono = verificar_monotonia_retornos(datos_nb["periodos_retorno"], cfg["periodos_retorno"])
    extra = comparar_con_maximo_historico(
        datos_nb["periodos_retorno"],
        max_hist,
        cfg["periodos_retorno"],
        cfg["criterios"]["ratio_q100_vs_max_historico_alerta"],
    )
    chk = checklist_consistencia(mono, extra, conflictos)
    chk.to_csv(out / "05_checklist_resultados.csv", index=False)

    tabla_reporte = rank[
        [
            "Rio",
            "Distribucion",
            "KS_stat",
            "KS_pvalue",
            "AD_stat",
            "AIC",
            "RMSE_prob",
            "MAE",
            "ranking_global",
            "ranking_AIC",
        ]
    ].sort_values(["Rio", "ranking_global"])
    tabla_reporte.to_csv(out / "06_tabla_reporte_seccion6.csv", index=False)

    mejor_aic = mejor_por_criterio(rank, "AIC")
    mejor_aic.to_csv(out / "07_mejor_modelo_por_rio_AIC.csv", index=False)

    for rio in cfg["rios"]:
        if rio in series:
            generar_graficas_rio(
                rio,
                series[rio],
                datos_nb["parametros"],
                datos_nb["periodos_retorno"],
                cfg["periodos_retorno"],
                graf_dir,
            )

    entrada_dist = PIPELINE_ROOT / cfg["entrada_distribuciones_equipo"]
    df_dist = cargar_resultados_distribuciones(entrada_dist)
    integrado = False
    if df_dist is not None:
        df_dist.to_csv(out / "08_resultados_paso4_integrados.csv", index=False)
        integrado = True

    comparacion_nb = datos_nb["mejor_aic"][["Rio", "Distribucion", "AIC"]].rename(
        columns={"Distribucion": "Dist_notebook_07", "AIC": "AIC_notebook_07"}
    )
    comparacion = mejor_aic[["Rio", "Distribucion", "AIC"]].merge(comparacion_nb, on="Rio")
    comparacion["coincide_con_notebook"] = comparacion["Distribucion"] == comparacion["Dist_notebook_07"]
    comparacion.to_csv(out / "09_validacion_cruzada_notebook.csv", index=False)

    meta = {
        "fase": 2,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "rios": cfg["rios"],
        "n_modelos_evaluados": int(len(ampliada)),
        "paso4_integrado": integrado,
        "salidas": [p.name for p in sorted(out.iterdir()) if p.is_file()],
    }
    (out / "manifest_fase2.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta

# Resumen del pipeline — Paso 6 (Axel)

**Proyecto:** Análisis de frecuencias de las entregas históricas del Río Bravo: comparación de distribuciones probabilísticas para extremos hidrológicos en una cuenca transfronteriza.

**Carpeta:** `pipeline_paso6_metricas/` (raíz del pipeline).

---

## Contexto del artículo (10 pasos)

| Paso | Contenido | Responsables | Relación con este pipeline |
|------|-----------|--------------|----------------------------|
| 1 | Introducción / deuda hídrica y extremos | Fernando, Alfonso | Marco (`Introduccion…pdf`, `propuesta.PNG`) |
| 2 | Base de datos y control de calidad | Fernando | `02_validacion.csv` |
| 3 | Series para frecuencias (anuales, estacionales, excedencias) | Cecilia Téllez, Carlos Franco | `01_maximos_anuales.csv` (anuales listos) |
| 4 | Distribuciones a comparar (13 modelos) | Ana Rosa, Kay, Cecy, Carlos | `Distribuciones/Probabilística.pdf` + CSV opcional en `entrada/` |
| 5 | Estimación de parámetros | Luis Fernando | Notebook + `04_parametros_estimados.csv` |
| **6** | **Métricas, errores y consistencia hidrológica** | **Axel** | **Este pipeline (2 fases)** |
| 7 | Periodos de retorno y sensibilidad | Diego Pallares, Braulio | `06_periodos_retorno.csv` |
| 8 | Incertidumbre | Kay García | Futura extensión del pipeline |
| 9–10 | Discusión y conclusiones | Varios | Redacción con salidas de fase 2 |

---

## Fuentes integradas (pasos 1–5)

1. **Notebook** `notebook_completo_analisis_frecuencias_hidrologicas.ipynb`  
   - 7 ríos/tributarios, periodo 1950–2025, n = 76.  
   - Distribuciones: Gumbel (momentos y MLE), Exponencial 1P/2P, GEV (MLE).  
   - Salidas en `resultados_frecuencias/01`–`07`.

2. **Documento paso 4** `Distribuciones/Probabilística.pdf`  
   - Gamma, Gumbel, Pareto, Burr XII, GEV, Kappa, LogNormal, Log-Pearson, Poisson-Exponencial, TCEV, Wakeby, Weibull, Normal.  
   - Se integran en fase 2 mediante `entrada/fase2_resultados_distribuciones.csv` (plantilla en `.example`).

3. **Especificación bifásica** `Métricas de ajuste, errores y consistencia hidrológica.docx`  
   - Fase 1: framework antes de recibir todos los resultados.  
   - Fase 2: aplicación, tablas, gráficas e interpretación crítica.

---

## Desarrollo bifásico implementado

### Fase 1 — Framework (antes de resultados completos)

**Comando:** `python run_pipeline.py --fase 1`

**Entregables** (`salidas/fase1/`):

| Archivo | Contenido |
|---------|-----------|
| `01_catalogo_metricas.csv` | RMSE, MAE, sesgo, logLik, AIC, BIC, KS, AD, ?² |
| `02_criterios_seleccion.csv` | Reglas de ranking y selección |
| `03_checklist_consistencia_hidrologica.csv` | Verificaciones H1–H4 |
| `04_mapa_integracion_pasos_1_5.csv` | Trazabilidad por paso del artículo |
| `05_brecha_distribuciones_paso4_vs_5.csv` | 13 vs 5 distribuciones |
| `manifest_fase1.json` | Metadatos de ejecución |

Documentación complementaria: `fase1/criterios_evaluacion.md`, `fase1/checklist_consistencia_hidrologica.md`.

### Fase 2 — Aplicación (con resultados recibidos)

**Comando:** `python run_pipeline.py --fase 2`

**Entradas mínimas:** CSV del notebook en `resultados_frecuencias/`.  
**Entrada opcional:** CSV unificado del equipo del paso 4.

**Entregables** (`salidas/fase2/`):

| Archivo | Contenido |
|---------|-----------|
| `01_metricas_ampliadas_notebook.csv` | Métricas del notebook + MAE, sesgo, AD, ?² |
| `02_ranking_modelos.csv` | Ranking por AIC, KS, RMSE, AD y score compuesto |
| `03_conflictos_entre_metricas.csv` | Discrepancias AIC vs KS vs RMSE por río |
| `04_tabla_comparativa_completa.csv` | Métricas + cuantiles Q_T |
| `05_checklist_resultados.csv` | Monotonía, extrapolación, aptitud hidrológica |
| `06_tabla_reporte_seccion6.csv` | Tabla tipo artículo: Distribución \| KS \| AD \| AIC \| RMSE \| Ranking |
| `07_mejor_modelo_por_rio_AIC.csv` | Mejor modelo por tributario |
| `08_resultados_paso4_integrados.csv` | Solo si existe CSV del paso 4 |
| `09_validacion_cruzada_notebook.csv` | Comparación con `07_tabla_final_mejor_aic.csv` |
| `graficas/{rio}/` | QQ plot, CDF empírica vs teórica, curva de periodos de retorno |
| `manifest_fase2.json` | Metadatos de ejecución |

**Hallazgo preliminar (ejecución sobre datos actuales):** para la mayoría de los ríos el **GEV (MLE)** domina en AIC y KS; en **San Diego** el notebook selecciona **Exponencial 2P** (mejor AIC con KS y RMSE aceptables). Conviene discutir en la sección 6 si el criterio hidrológico refuerza o modifica esa elección.

---

## Cómo ejecutar

```bash
cd pipeline_paso6_metricas
pip install -r requirements.txt
python run_pipeline.py --fase all
```

Configuración de rutas, rios, pesos del ranking y umbrales: `config.yaml`.

---

## Próximos pasos sugeridos

1. Exportar resultados MATLAB del paso 4 al formato `entrada/fase2_resultados_distribuciones.csv`.
2. Incorporar **máximos estacionales** y **excedencias** cuando Cecilia/Carlos entreguen las series.
3. Conectar con paso 7 (sensibilidad de Q_T) y paso 8 (intervalos de confianza).
4. Redactar la sección 6 del artículo usando `06_tabla_reporte_seccion6.csv` y el análisis de conflictos.

---

*Generado como marco reproducible para el paso 6 — métricas de ajuste, errores y consistencia hidrológica (pruebas de bondad de ajuste).*

# Resumen del pipeline actual — Paso 6

**Proyecto:** Análisis de frecuencias de las entregas históricas del Río Bravo: comparación de distribuciones probabilísticas para extremos hidrológicos en una cuenca transfronteriza.

**Carpeta:** `pipeline_paso6_metricas/` (raíz del pipeline).

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

**Hallazgo preliminar (ejecución sobre datos actuales):** para la mayoría de los ríos el **GEV (MLE)** domina en AIC y KS; en **San Diego** el notebook selecciona **Exponencial 2P** (mejor AIC con KS y RMSE aceptables). Conviene discutir en la sección 6 si el criterio hidrológico refuerza o modifica esa elección.

---

## Cómo ejecutar

```bash
cd pipeline_paso6_metricas
pip install -r requirements.txt
python run_pipeline.py --fase all
```

Configuración de rutas, rios, pesos del ranking y umbrales: `config.yaml`.


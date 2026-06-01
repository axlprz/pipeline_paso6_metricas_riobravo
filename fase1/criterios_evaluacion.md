# Criterios de evaluación y selección de modelos (Fase 1)

## Objetivo del paso 6

Evaluar qué distribuciones representan mejor los **máximos anuales** (y, en fases posteriores, máximos estacionales y excedencias) de las entregas históricas del Río Bravo, combinando criterios **estadísticos**, **hidrológicos** y **operativos**.

## Definición de “buen ajuste”

| Dimensión | Criterio |
|-----------|----------|
| Estadístico | Bajos AIC/BIC, RMSE en probabilidades, pruebas KS/AD/?² no significativas |
| Hidrológico | Colas razonables, Q_T crecientes, Q_100 no desconectado del máximo observado |
| Operativo | Estabilidad paramétrica y utilidad para planificación binacional (enlace con pasos 7–9) |

## Ranking

1. **AIC** (criterio principal del notebook de Luis Fernando).
2. **KS** y **RMSE_prob** (ajuste global y en cola).
3. **Score compuesto** (pesos en `config.yaml`) para desempate.
4. **Checklist hidrológico** como filtro final, no como único criterio.

## Integración con pasos 4 y 7

- **Paso 4** : 13 distribuciones ajustadas en MATLAB.
- **Paso 5** : 5 distribuciones con salidas CSV en `resultados_frecuencias/`.
- **Paso 7**: usar `06_periodos_retorno.csv` y salidas `07_*` para sensibilidad por modelo.

# Checklist de consistencia hidrológica (Fase 1)

Aplicar por cada combinación **Río × Distribución × Tipo de serie**.

- [ ] **H1 — Monotonía:** Q_T_2 ? Q_T_5 ? … ? Q_T_100.
- [ ] **H2 — Extrapolación:** Q_T_100 ? ratio × máximo histórico (ratio por defecto: 5; ver `config.yaml`).
- [ ] **H3 — Eventos históricos:** la cola modelada no contradice picos documentados (p. ej. 1958 en agregado de tributarios).
- [ ] **H4 — Concordancia de métricas:** si AIC, KS y RMSE no coinciden en el “mejor” modelo, documentar el conflicto en la discusión.

## Preguntas guía (documento Word del paso 6)

1. ¿La cola de la distribución es físicamente razonable?
2. ¿Predice valores extremos absurdos?
3. ¿El periodo de retorno crece de forma coherente?
4. ¿Es coherente con literatura del Río Bravo o cuencas áridas/semiáridas comparables?

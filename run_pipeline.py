#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pipeline paso 6: metricas de ajuste y consistencia hidrologica (Rio Bravo)."""
from __future__ import annotations

import argparse
import sys

from src.config import load_config
from src.pipeline import ejecutar_fase1, ejecutar_fase2


def main():
    parser = argparse.ArgumentParser(description="Pipeline paso 6 - Rio Bravo")
    parser.add_argument(
        "--fase",
        choices=["1", "2", "all"],
        default="all",
        help="Fase 1: framework; Fase 2: aplicacion; all: ambas",
    )
    args = parser.parse_args()
    cfg = load_config()
    resultados = []
    if args.fase in ("1", "all"):
        print("Ejecutando Fase 1 (framework de evaluacion)...")
        resultados.append(ejecutar_fase1(cfg))
    if args.fase in ("2", "all"):
        print("Ejecutando Fase 2 (metricas sobre resultados pasos 1-5)...")
        resultados.append(ejecutar_fase2(cfg))
    for r in resultados:
        print(f"  -> fase {r['fase']} completada ({r['fecha']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

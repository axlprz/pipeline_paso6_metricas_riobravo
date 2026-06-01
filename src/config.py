from __future__ import annotations

from pathlib import Path

import yaml

PIPELINE_ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    path = PIPELINE_ROOT / "config.yaml"
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_pipeline_root"] = PIPELINE_ROOT
    cfg["_proyecto_raiz"] = (PIPELINE_ROOT / cfg["proyecto_raiz"]).resolve()
    return cfg


def resolve_path(cfg: dict, key: str) -> Path:
    rel = cfg["fuentes"][key]
    return (PIPELINE_ROOT / rel).resolve()


def salida_dir(cfg: dict, fase: str) -> Path:
    d = PIPELINE_ROOT / cfg["salidas"][fase]
    d.mkdir(parents=True, exist_ok=True)
    return d

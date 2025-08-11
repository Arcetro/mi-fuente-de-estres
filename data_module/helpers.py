import json
from pathlib import Path
from typing import Any, Dict, Optional

from rapidfuzz import process, fuzz


BASE_DIR = Path(__file__).resolve().parent


def _load_json(name: str) -> Any:
    with open(BASE_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


_POLICIES = None
_TEMPLATES = None
_CATALOGO = None


def getPoliticas() -> Dict[str, Any]:
    global _POLICIES
    if _POLICIES is None:
        _POLICIES = _load_json("policies.json")
    return _POLICIES


def getTemplates() -> Dict[str, Any]:
    global _TEMPLATES
    if _TEMPLATES is None:
        _TEMPLATES = _load_json("templates.json")
    return _TEMPLATES


def getPlantilla(template_id: str) -> str:
    templates = getTemplates()
    return templates.get(template_id, "")


def getCatalogo() -> Dict[str, Any]:
    global _CATALOGO
    if _CATALOGO is None:
        _CATALOGO = _load_json("catalogo_unidades.json")
    return _CATALOGO


def getUnidadByTexto(text: str) -> Optional[str]:
    text = (text or "").strip().lower()
    if not text:
        return None
    catalogo = getCatalogo()
    enum_ids = list(catalogo.keys())
    labels = []
    for eid, meta in catalogo.items():
        labels.append((eid, meta.get("etiqueta_publica", "").lower()))
        for s in meta.get("sinonimos", []):
            labels.append((eid, s.lower()))
    # search best match per eid
    best_eid = None
    best_score = -1.0
    for eid, label in labels:
        score = fuzz.ratio(text, label) / 100.0
        if score > best_score:
            best_score = score
            best_eid = eid
    return best_eid if (best_score >= 0.85) else None


def getCapacidad(unidad: str) -> Optional[int]:
    meta = getCatalogo().get(unidad)
    return int(meta.get("capacidad_max")) if meta else None


def getTarifa(unidad: str) -> Optional[float]:
    # Dummy fixed tariffs per unit id
    tariffs = {
        "studio": 50.0,
        "doble": 70.0,
        "triple": 90.0,
        "familiar": 120.0,
        "suite": 110.0,
        "depto_2amb": 150.0,
        "cabaña_1hab": 130.0,
    }
    return tariffs.get(unidad)



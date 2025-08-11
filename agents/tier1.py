import re
from typing import Any, Tuple

from pic.contracts import PICMessage, T1Output, Intent
from policy.core import validateSlot
from data_module.helpers import getUnidadByTexto


_INTENT_PATTERNS = [
    (Intent.SALUDO, re.compile(r"\b(hola|buenas)\b", re.I)),
    (Intent.DESPEDIDA, re.compile(r"\b(gracias|chau|hasta luego)\b", re.I)),
    (Intent.UBICACION, re.compile(r"\b(dónde|donde)\b.*\b(están|ubicación|ubicacion)\b", re.I)),
    (Intent.POLITICAS, re.compile(r"check[- ]?in|check[- ]?out|horario", re.I)),
    (Intent.CONSULTA_PRECIO, re.compile(r"precio|cuánto sale|cuanto sale|tarifa", re.I)),
    (Intent.DISPONIBILIDAD, re.compile(r"hay lugar|disponibilidad", re.I)),
]


def _classify_intent(text: str) -> Tuple[Intent, float, float]:
    text = text or ""
    matches = [intent for intent, pat in _INTENT_PATTERNS if pat.search(text)]
    if not matches:
        return Intent.OTRO, 0.4, 0.3
    intent = matches[0]
    confidence = 0.9 if len(matches) == 1 else 0.6
    complexity = 0.7 if len(matches) > 1 or len(text) > 200 else 0.3
    return intent, confidence, complexity


def _extract_entities(text: str) -> dict:
    entities = {
        "checkin": None,
        "noches": None,
        "personas": None,
        "tipo_unidad": None,
    }
    # checkin date dd/mm[/yyyy]
    m = re.search(r"(\d{1,2}/\d{1,2}(?:/\d{2,4})?)", text)
    if m:
        ok, norm = validateSlot("checkin", m.group(1), "es-AR")
        if ok:
            entities["checkin"] = norm
    # noches
    m = re.search(r"(\d{1,2})\s*(noches?|noche)\b", text, re.I)
    if m:
        ok, norm = validateSlot("noches", m.group(1), "es-AR")
        if ok:
            entities["noches"] = norm
    # personas
    m = re.search(r"(\d{1,2})\s*(personas?|pax)\b", text, re.I)
    if m:
        ok, norm = validateSlot("personas", m.group(1), "es-AR")
        if ok:
            entities["personas"] = norm
    # tipo_unidad
    m = re.search(r"(studio|doble|triple|familiar|suite|depto\s*2\s*amb|cabañ?a\s*1\s*hab|matrimonial|monoambiente)", text, re.I)
    if m:
        enum_id = getUnidadByTexto(m.group(1))
        if enum_id:
            entities["tipo_unidad"] = enum_id
    return entities


def handle(msg: PICMessage) -> T1Output:
    text = (msg.payload or {}).get("text", "")
    intent, confidence, complexity = _classify_intent(text)
    entities = _extract_entities(text)
    # detect USD request terms for downstream handling
    risk_flags = []
    if any(t in text.lower() for t in ["usd", "dolar", "dólar", "dolares", "dólares"]):
        risk_flags.append("usd_request")
    return T1Output(
        intent=intent,
        confidence=confidence,
        entities=entities,  # type: ignore[arg-type]
        complexity_score=complexity,
        risk_flags=risk_flags,
        reasons="deterministic-mock",
    )



from typing import Any, Dict

from pic.contracts import PICMessage, T1Output, T2Output, Intent, Brief
import os
from data_module.helpers import getPoliticas, getPlantilla, getTarifa, getCapacidad
from policy.core import buildReprompt


def _has_min_entities(entities: dict) -> bool:
    required = ["checkin", "noches", "personas", "tipo_unidad"]
    return all(entities.get(k) not in (None, "") for k in required)


def _respond_canonical(intent: Intent, entities: dict) -> T2Output:
    if intent == Intent.POLITICAS:
        pol = getPoliticas()
        text = getPlantilla("POLITICAS").format(checkin=pol["checkin"], checkout=pol["checkout"])
    elif intent == Intent.UBICACION:
        text = getPlantilla("UBICACION")
    elif intent == Intent.SALUDO:
        text = getPlantilla("SALUDO")
    elif intent == Intent.DESPEDIDA:
        text = getPlantilla("DESPEDIDA")
    else:
        text = getPlantilla("GENERICA")
    return T2Output(
        intent=intent,
        confidence=0.9,
        entities=entities,
        brief=Brief(summary=text),
        next_action="respond",
    )


def _respond_quote(entities: dict) -> T2Output:
    unidad = entities["tipo_unidad"]
    tarifa_ars = (getTarifa(unidad) or 0.0) * 1000  # dummy ARS
    precio_ars = round(tarifa_ars * float(entities["noches"]), 2)
    moneda = "ARS"
    precio = precio_ars
    text = getPlantilla("COTIZACION").format(
        tipo_unidad=unidad,
        personas=entities["personas"],
        noches=entities["noches"],
        checkin=entities["checkin"],
        precio=f"{precio}",
        moneda=moneda,
    )
    return T2Output(
        intent=Intent.CONSULTA_PRECIO,
        confidence=0.9,
        entities=entities,
        brief=Brief(summary=text),
        next_action="respond",
    )


def handle(msg: PICMessage) -> Dict[str, Any]:
    t1_payload = (msg.payload or {}).get("t1")
    if not t1_payload:
        return {"error": "missing T1 output"}
    t1 = T1Output.model_validate(t1_payload)
    entities = t1.entities.model_dump()  # type: ignore[assignment]

    if t1.intent in {Intent.POLITICAS, Intent.UBICACION, Intent.SALUDO, Intent.DESPEDIDA}:
        out = _respond_canonical(t1.intent, entities)
        return out.model_dump()

    if t1.intent in {Intent.CONSULTA_PRECIO, Intent.DISPONIBILIDAD}:
        # Detect USD request via risk_flags from T1
        if "usd_request" in (t1.risk_flags or []):
            from telemetry.metrics import COUNTERS
            COUNTERS["usd_request"].inc()
            info = getPlantilla("currency_info")
            # If we also have full entities, we emulate two messages by concatenating summaries
            if _has_min_entities(entities):
                quote = _respond_quote(entities)
                merged = quote.brief.summary + "\n" + info
                return T2Output(
                    intent=t1.intent,
                    confidence=0.9,
                    entities=entities,
                    brief=Brief(summary=merged),
                    next_action="respond",
                ).model_dump()
            # Otherwise only info
            return T2Output(
                intent=t1.intent,
                confidence=0.9,
                entities=entities,
                brief=Brief(summary=info),
                next_action="respond",
            ).model_dump()
        # DISPONIBILIDAD simple: si hay fecha/noches/personas, responder genérico aunque falte unidad
        if t1.intent == Intent.DISPONIBILIDAD:
            have_basic = all(entities.get(k) not in (None, "") for k in ("checkin", "noches", "personas"))
            if have_basic:
                text = f"Tenemos disponibilidad para {entities['personas']} persona(s) desde {entities['checkin']} por {entities['noches']} noche(s)."
                return T2Output(
                    intent=t1.intent,
                    confidence=0.9,
                    entities=entities,
                    brief=Brief(summary=text),
                    next_action="respond",
                ).model_dump()
        # capacity check
        cap = getCapacidad(entities.get("tipo_unidad")) if entities.get("tipo_unidad") else None
        if cap is not None and entities.get("personas") and int(entities["personas"]) > cap:
            # suggest upgrade: triple -> familiar
            sug = "triple" if cap < 3 else "familiar"
            return T2Output(
                intent=t1.intent,
                confidence=0.9,
                entities=entities,
                brief=Brief(summary=f"Capacidad insuficiente para {entities.get('tipo_unidad')}. Sugerencia: {sug}"),
                next_action="respond",
            ).model_dump()
        if _has_min_entities(entities):
            out = _respond_quote(entities)
            return out.model_dump()
        # reprompt for first missing slot
        required = {"checkin": True, "noches": True, "personas": True, "tipo_unidad": True}
        attempts = 1
        rep = buildReprompt(required, entities, msg.context.locale, attempts)
        return {
            "brief": {"summary": "reprompt", "gaps": []},
            "entities": entities,
            "next_action": "reprompt",
            "reprompt": rep,
            "intent": t1.intent.value,
            "confidence": t1.confidence,
        }

    # default
    return _respond_canonical(Intent.OTRO, entities).model_dump()



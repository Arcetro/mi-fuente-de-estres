from pic.contracts import PICMessage
from pic.bus import PicBus
from agents import tier1, tier2
from telemetry.metrics import COUNTERS

bus = PicBus(routes={"tier1": tier1.handle, "tier2": tier2.handle})

def process_message(pic: PICMessage) -> dict:
    """
    Processes a message, handling routing and escalation between agent tiers.
    """
    t1 = bus.route(pic)

    # Escalate to tier2 when needed
    to_t2 = t1.intent not in {t1.intent.SALUDO, t1.intent.DESPEDIDA, t1.intent.UBICACION, t1.intent.POLITICAS} or (
        t1.confidence < 0.8 or t1.complexity_score >= 0.6
    )

    if to_t2:
        COUNTERS["t1_to_t2_escalations"].inc()
        pic.to = "tier2"
        pic.payload = {"t1": t1.model_dump()}
        t2 = bus.route(pic)
        return {"status": "ok", "t2": t2}

    return {"status": "ok", "t1": t1.model_dump()}

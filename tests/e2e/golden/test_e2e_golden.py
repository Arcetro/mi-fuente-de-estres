from pic.contracts import PICMessage, PICContext
from pic.bus import PicBus
from agents import tier1, tier2


def _pic(text: str) -> PICMessage:
    return PICMessage(id="g1", from_="wa", to="tier1", context=PICContext(sessionId="golden"), payload={"text": text})


def test_golden_saludo():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("hola")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "respond"


def test_golden_ubicacion():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("dónde están?")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "respond"


def test_golden_precio_completo():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio studio 12/09/2025 2 noches 2 personas")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "respond"


def test_golden_precio_falta_noches():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio studio 12/09 2 personas")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "reprompt"
    assert t2["reprompt"]["slot"] == "noches"


def test_golden_disponibilidad_simple():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("hay lugar 20/10 2 noches 3 personas")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "respond"


def test_golden_capacidad_insuficiente_upgrade():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio doble 12/09 2 noches 3 personas")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "respond"
    assert "Sugerencia" in t2["brief"]["summary"]


def test_golden_unidad_ambigua_reprompt():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio matrimonial o similar 12/09 2 noches 2 personas")
    t1 = bus.route(msg)
    # Mapa fuzzy debería resolver a doble; si no, reprompt
    if t1.entities.tipo_unidad is None:
        msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
        t2 = bus.route(msg)
        assert t2["next_action"] == "reprompt" and t2["reprompt"]["slot"] == "tipo_unidad"
    else:
        assert t1.entities.tipo_unidad in ("doble", "studio")


def test_golden_usd_on_demand(monkeypatch):
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio studio 12/09 2 noches 2 personas ¿me lo pasás en dólares?")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    # Debe responder en ARS y agregar mensaje informativo de moneda
    assert "ARS" in t2["brief"]["summary"]
    assert "Trabajamos en ARS" in t2["brief"]["summary"]
    assert "USD ref." not in t2["brief"]["summary"]


def test_golden_dedupe_idempotencia():
    # This test simulates idempotency at adapter level; here we just ensure t2 computed once is stable.
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio studio 12/09 2 noches 2 personas")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2a = bus.route(msg)
    t2b = bus.route(msg)
    assert t2a["brief"]["summary"] == t2b["brief"]["summary"]



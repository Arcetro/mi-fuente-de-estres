from pic.contracts import PICMessage, PICContext
from pic.bus import PicBus
from agents import tier1, tier2


def _pic(text: str) -> PICMessage:
    return PICMessage(id="1", from_="wa", to="tier1", context=PICContext(sessionId="s"), payload={"text": text})


def test_tier2_saludo_respond():
    bus = PicBus(routes={"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("hola")
    t1 = bus.route(msg)
    msg.to = "tier2"
    msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "respond"
    assert "Hola" in t2["brief"]["summary"]


def test_tier2_quote_full():
    bus = PicBus(routes={"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio studio 12/09/2025 2 noches 2 personas")
    t1 = bus.route(msg)
    msg.to = "tier2"
    msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "respond"
    assert "studio" in t2["brief"]["summary"].lower()


def test_tier2_quote_missing_one_slot_reprompt():
    bus = PicBus(routes={"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio studio 12/09 2 personas")  # falta noches
    t1 = bus.route(msg)
    msg.to = "tier2"
    msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert t2["next_action"] == "reprompt"
    assert t2["reprompt"]["slot"] == "noches"


def test_tier2_usd_request_informative():
    bus = PicBus({"tier1": tier1.handle, "tier2": tier2.handle})
    msg = _pic("precio studio 12/09 2 noches 2 personas en USD")
    t1 = bus.route(msg)
    msg.to = "tier2"; msg.payload = {"t1": t1.model_dump()}
    t2 = bus.route(msg)
    assert "Trabajamos en ARS" in t2["brief"]["summary"]
    assert "USD ref." not in t2["brief"]["summary"]



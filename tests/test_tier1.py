from pic.contracts import PICMessage, PICContext, Intent
from agents import tier1


def _msg(text: str) -> PICMessage:
    return PICMessage(id="1", from_="wa", to="tier1", context=PICContext(sessionId="s"), payload={"text": text})


def test_tier1_intent_saludo():
    out = tier1.handle(_msg("hola"))
    assert out.intent == Intent.SALUDO and out.confidence >= 0.6


def test_tier1_entities_parse():
    out = tier1.handle(_msg("precio studio 12/09 2 noches 2 personas"))
    assert out.entities.checkin is not None
    assert out.entities.noches == 2
    assert out.entities.personas == 2
    assert out.entities.tipo_unidad == "studio"



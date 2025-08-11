from datetime import datetime, timedelta
import time as _time

from policy.core import buildReprompt, validateSlot, SessionStore, COOLDOWN_SECONDS


def test_build_reprompt_order_and_format():
    required = {"checkin": True, "noches": True, "personas": True, "tipo_unidad": True}
    collected = {"checkin": None, "noches": None, "personas": None, "tipo_unidad": None}
    payload = buildReprompt(required, collected, "es-AR", attempts=1)
    assert payload["type"] == "REPROMPT"
    assert payload["slot"] == "checkin"
    assert len(payload["question"]) <= 120
    assert payload["max_attempts"] == 2

    collected["checkin"] = "2025-09-12"
    payload2 = buildReprompt(required, collected, "es-AR", attempts=2)
    assert payload2["slot"] == "noches"
    assert payload2["validation"]["type"] in ("integer", "date", "enum")


def test_validate_slot_date_and_numbers_and_enum():
    ok, norm = validateSlot("checkin", "12/09/2025", "es-AR")
    assert ok and norm == "2025-09-12"

    ok, norm = validateSlot("checkin", "12/09", "es-AR")
    assert ok and len(norm) == 10

    ok, norm = validateSlot("noches", "2", "es-AR")
    assert ok and norm == 2

    ok, norm = validateSlot("personas", "3", "es-AR")
    assert ok and norm == 3

    ok, norm = validateSlot("tipo_unidad", "matrimonial", "es-AR")
    assert ok and norm == "doble"


def test_session_store_ttl_and_inactivity_and_cooldown(monkeypatch):
    store = SessionStore(ttl_hours=0, inactivity_hours=0)  # force expiry checks
    s = store.get("u1")
    assert s.createdAt <= s.lastSeen

    # simulate inactivity expiry by setting lastSeen in the past
    s.lastSeen = datetime.utcnow() - timedelta(hours=3)
    store.set("u1", s)
    s2 = store.get("u1")
    assert s2.createdAt >= s.createdAt  # got reset

    # cooldown
    assert store.can_reprompt("u1") is True
    store.mark_reprompt("u1")
    assert store.can_reprompt("u1") is False
    # fast-forward cooldown
    s3 = store.get("u1")
    s3.lastPromptAtMono -= (COOLDOWN_SECONDS + 1)
    store.set("u1", s3)
    assert store.can_reprompt("u1") is True



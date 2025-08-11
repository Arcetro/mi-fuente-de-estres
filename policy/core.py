from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import re
from typing import Any, Dict, Optional, Tuple, List, Callable

from dateutil import parser as date_parser

from data_module.helpers import (
    getUnidadByTexto,
)


COOLDOWN_SECONDS = 30
MAX_ATTEMPTS_PER_SLOT = 2
SLOT_ORDER = ["checkin", "noches", "personas", "tipo_unidad"]


def _build_validation(slot: str) -> Dict[str, Any]:
    if slot == "checkin":
        return {"type": "date"}
    if slot == "noches":
        return {"type": "integer", "min": 1, "max": 30}
    if slot == "personas":
        return {"type": "integer", "min": 1, "max": 8}
    if slot == "tipo_unidad":
        # The enum list is resolved at runtime by data_module; leave empty here.
        return {"type": "enum"}
    return {}


def _build_question(slot: str) -> Tuple[str, List[str]]:
    if slot == "noches":
        return (
            "¿Cuántas noches pensás quedarte?",
            ["1", "2", "3", "4", "5+"],
        )
    if slot == "checkin":
        return ("¿Para qué fecha querés alojarte? (dd/mm)", [])
    if slot == "personas":
        return (
            "¿Para cuántas personas sería?",
            ["1", "2", "3", "4", "5+"],
        )
    if slot == "tipo_unidad":
        return (
            "¿Preferís studio o doble?",
            ["Studio", "Doble", "Otra"],
        )
    return ("", [])


def buildReprompt(
    required: Dict[str, Any],
    collected: Dict[str, Any],
    locale: str,
    attempts: int,
) -> Dict[str, Any]:
    missing = [s for s in SLOT_ORDER if required.get(s) and (collected.get(s) in (None, ""))]
    slot = missing[0] if missing else None
    if slot is None:
        # Nothing to reprompt
        return {
            "type": "REPROMPT",
            "slot": None,
            "question": "",
            "quick_replies": [],
            "validation": {},
            "attempt": attempts,
            "max_attempts": MAX_ATTEMPTS_PER_SLOT,
        }

    question, quick_replies = _build_question(slot)
    question = question[:120]
    payload = {
        "type": "REPROMPT",
        "slot": slot,
        "question": question,
        "quick_replies": quick_replies,
        "validation": _build_validation(slot),
        "attempt": attempts,
        "max_attempts": MAX_ATTEMPTS_PER_SLOT,
    }
    return payload


_DATE_RE = re.compile(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?$")


def _parse_date_es(value: str) -> Optional[str]:
    m = _DATE_RE.match(value.strip())
    if not m:
        return None
    dd, mm, yyyy = m.groups()
    day = int(dd)
    month = int(mm)
    if yyyy is None:
        year = datetime.utcnow().year
    else:
        y = int(yyyy)
        year = 2000 + y if len(yyyy) == 2 else y
    try:
        dt = datetime(year, month, day)
    except ValueError:
        return None
    return dt.date().isoformat()


def validateSlot(slot_name: str, value: Any, locale: str) -> Tuple[bool, Any | str]:
    if slot_name == "checkin":
        if isinstance(value, str):
            iso = _parse_date_es(value)
            return (True, iso) if iso else (False, "Formato de fecha inválido (dd/mm[/aaaa])")
        return (False, "Valor inválido para fecha")
    if slot_name == "noches":
        try:
            n = int(str(value).strip())
            if 1 <= n <= 30:
                return True, n
            return False, "Noches fuera de rango (1-30)"
        except Exception:
            return False, "Noches deben ser un entero"
    if slot_name == "personas":
        try:
            p = int(str(value).strip())
            if 1 <= p <= 8:
                return True, p
            return False, "Personas fuera de rango (1-8)"
        except Exception:
            return False, "Personas deben ser un entero"
    if slot_name == "tipo_unidad":
        if not isinstance(value, str) or not value.strip():
            return False, "Unidad inválida"
        enum_id = getUnidadByTexto(value)
        if enum_id:
            return True, enum_id
        return False, "Unidad desconocida"
    return False, "Slot desconocido"


@dataclass
class SessionState:
    pending_slot: Optional[str] = None
    attempts: Dict[str, int] = field(default_factory=dict)
    collected: Dict[str, Any] = field(default_factory=dict)
    createdAt: datetime = field(default_factory=lambda: datetime.utcnow())
    lastSeen: datetime = field(default_factory=lambda: datetime.utcnow())
    lastPromptAtMono: float = field(
        default_factory=lambda: time.monotonic() - (COOLDOWN_SECONDS + 1)
    )


class SessionStore:
    def __init__(self, ttl_hours: int = 12, inactivity_hours: int = 2):
        self._store: Dict[str, SessionState] = {}
        self.ttl = timedelta(hours=ttl_hours)
        self.inactivity = timedelta(hours=inactivity_hours)

    def get(self, session_id: str) -> SessionState:
        now = datetime.utcnow()
        state = self._store.get(session_id)
        if state is None:
            state = SessionState()
            self._store[session_id] = state
            return state
        if now - state.createdAt > self.ttl:
            # reset TTL expiry
            state = SessionState()
            self._store[session_id] = state
            return state
        if now - state.lastSeen > self.inactivity:
            # mark inactive -> reset
            state = SessionState()
            self._store[session_id] = state
            return state
        state.lastSeen = now
        return state

    def set(self, session_id: str, state: SessionState) -> None:
        self._store[session_id] = state

    def reset(self, session_id: str) -> None:
        self._store[session_id] = SessionState()

    def can_reprompt(self, session_id: str) -> bool:
        # Do not trigger TTL/inactivity reset for cooldown check
        state = self._store.get(session_id)
        if state is None:
            state = SessionState()
            self._store[session_id] = state
        elapsed = time.monotonic() - state.lastPromptAtMono
        return elapsed >= COOLDOWN_SECONDS

    def mark_reprompt(self, session_id: str) -> None:
        # Do not trigger TTL/inactivity reset for cooldown update
        state = self._store.get(session_id)
        if state is None:
            state = SessionState()
        state.lastPromptAtMono = time.monotonic()
        self._store[session_id] = state




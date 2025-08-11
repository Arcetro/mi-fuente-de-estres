import pytest
from pydantic import ValidationError

from pic.contracts import (
    Intent,
    MessageType,
    PICContext,
    PICMessage,
    T1Output,
    T2Output,
    Brief,
)


def test_pic_message_valid():
    msg = PICMessage(
        id="123",
        from_="wa-adapter",
        to="tier1",
        context=PICContext(sessionId="user-1"),
        payload={"text": "hola"},
    )
    assert msg.version == "pic.v1"
    assert msg.type == MessageType.REQUEST
    assert msg.context.locale == "es-AR"
    assert msg.trace == []


def test_pic_message_invalid_extra_field():
    with pytest.raises(ValidationError):
        PICMessage(
            id="123",
            from_="wa-adapter",
            to="tier1",
            context=PICContext(sessionId="user-1"),
            payload={"text": "hola"},
            unknown=1,  # type: ignore
        )


def test_t1_output_valid():
    out = T1Output(intent=Intent.SALUDO, confidence=0.9, reasons="ok")
    assert out.entities.checkin is None
    assert out.risk_flags == []
    assert out.complexity_score == 0.0


def test_t1_output_invalid_missing_fields():
    with pytest.raises(ValidationError):
        T1Output(confidence=0.9, reasons="ok")  # type: ignore


def test_t2_output_valid():
    out = T2Output(
        intent=Intent.OTRO,
        confidence=0.5,
        entities={},
        brief=Brief(summary="..."),
        next_action="respond",
    )
    assert out.brief.gaps == []


def test_t2_output_invalid_next_action():
    with pytest.raises(ValidationError):
        T2Output(  # type: ignore
            intent=Intent.OTRO,
            confidence=0.5,
            entities={},
            brief=Brief(summary="..."),
            next_action="invalid",
        )



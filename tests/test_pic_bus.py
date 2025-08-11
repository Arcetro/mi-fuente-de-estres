import time
import pytest

from pic.contracts import PICContext, PICMessage
from pic.bus import PicBus


def dummy_handler(msg: PICMessage):
    # simulate small work
    time.sleep(0.001)
    return {"ok": True, "to": msg.to}


def test_bus_route_happy_path():
    msg = PICMessage(id="1", from_="tester", to="tier1", context=PICContext(sessionId="s1"))
    bus = PicBus(routes={"tier1": dummy_handler})
    result = bus.route(msg)
    assert result["ok"] is True
    assert msg.trace and msg.trace[-1]["node"] == "tier1"
    assert msg.trace[-1]["lat_ms"] >= 0


def test_bus_route_unknown_target():
    msg = PICMessage(id="1", from_="tester", to="unknown", context=PICContext(sessionId="s1"))
    bus = PicBus(routes={})
    with pytest.raises(ValueError) as ei:
        bus.route(msg)
    assert "unknown target" in str(ei.value)



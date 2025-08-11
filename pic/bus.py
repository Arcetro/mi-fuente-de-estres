import time
from typing import Callable, Dict, Any

from pic.contracts import PICMessage


class PicBus:
    """In-process router that dispatches based on the `to` field.

    Records latency and node in the message trace.
    """

    def __init__(self, routes: Dict[str, Callable[[PICMessage], Any]]):
        self.routes = routes

    def route(self, msg: PICMessage) -> Any:
        start = time.perf_counter()
        target = msg.to
        if target not in self.routes:
            raise ValueError(f"unknown target '{target}'")
        handler = self.routes[target]
        result = handler(msg)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        msg.trace.append({"node": target, "lat_ms": round(elapsed_ms, 3)})
        return result


def load_routes_from_env(json_str: str):
    """Stub for future HTTP route loader using PIC_ROUTES_JSON.

    This is intentionally a no-op placeholder for Milestone 1.
    """
    # TODO: Implement in Milestone 2+ when HTTP dispatch is needed.
    return {}



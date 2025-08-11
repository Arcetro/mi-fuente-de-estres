from __future__ import annotations

import time
import json
from contextlib import contextmanager
from typing import Iterator, Optional, Dict

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


HISTOGRAMS = {
    "pic_bus": Histogram("pic_bus_latency_ms", "Latency of pic bus route", buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000)),
    "tier1_handle": Histogram("tier1_handle_latency_ms", "Latency of tier1 handle", buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000)),
    "tier2_handle": Histogram("tier2_handle_latency_ms", "Latency of tier2 handle", buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000)),
    "wa_inbound": Histogram("wa_inbound_latency_ms", "Latency of wa inbound", buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000)),
    "wa_send": Histogram("wa_send_latency_ms", "Latency of wa send", buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000)),
}

COUNTERS = {
    "t1_to_t2_escalations": Counter("t1_to_t2_escalations_total", "Number of escalations from T1 to T2"),
    "reprompts": Counter("reprompts_total", "Number of reprompts emitted", ["slot"]),
    "dedupe_hits": Counter("dedupe_hits_total", "Number of inbound dedupe hits"),
    "usd_request": Counter("usd_request_total", "Number of USD currency requests detected"),
}


@contextmanager
def time_histogram(name: str, labels: Optional[Dict[str, str]] = None) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        # Basic histogram without labels
        HISTOGRAMS[name].observe(elapsed_ms)


def metrics_response():
    return CONTENT_TYPE_LATEST, generate_latest()


def json_log(message: str, **fields):
    rec = {"message": message, **fields}
    print(json.dumps(rec, ensure_ascii=False))



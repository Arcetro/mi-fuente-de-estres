from __future__ import annotations

import hmac
import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple

import httpx

from telemetry.metrics import time_histogram, COUNTERS, json_log


def verify_signature(app_secret: str, raw_body: bytes, signature_header: Optional[str]) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    provided = signature_header.split("=", 1)[1]
    digest = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(provided, digest)


def normalize_inbound(event: Dict[str, Any]) -> Dict[str, Any]:
    # Support text and interactive.button
    entry = (event.get("entry") or [{}])[0]
    changes = (entry.get("changes") or [{}])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])
    if not messages:
        return {"text": "", "sessionId": "", "locale": "es-AR", "wa_message_id": "", "qr_id": None}
    msg = messages[0]
    from_id = msg.get("from", "")
    conv_id = msg.get("context", {}).get("id")
    session_id = f"{from_id}:{conv_id}" if conv_id else from_id
    wa_message_id = msg.get("id", "")
    qr_id = None
    text = ""
    if msg.get("type") == "text":
        text = (msg.get("text") or {}).get("body", "")
    elif msg.get("type") == "interactive":
        inter = msg.get("interactive", {})
        if inter.get("type") == "button":
            reply = (inter.get("button_reply") or {})
            text = reply.get("title", "")
            qr_id = reply.get("id")
    return {
        "text": text,
        "sessionId": session_id,
        "locale": "es-AR",
        "wa_message_id": wa_message_id,
        "qr_id": qr_id,
    }


async def send_text(wa_base_url: str, token: str, to: str, body_text: str, request_id: str = "", session_id: str = "", client: Optional[httpx.AsyncClient] = None) -> Tuple[int, Any]:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body_text},
    }
    json_log("wa_send_text", request_id=request_id, sessionId=session_id, to=to)
    return await _post_with_backoff(wa_base_url, token, payload, "wa_send", client)


def build_quick_replies(to: str, question: str, buttons: Dict[str, str]):
    return {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": question},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": bid, "title": title}}
                    for bid, title in buttons.items()
                ]
            },
        },
    }


async def send_buttons(wa_base_url: str, token: str, to: str, question: str, qr_buttons: Dict[str, str], request_id: str = "", session_id: str = "", client: Optional[httpx.AsyncClient] = None) -> Tuple[int, Any]:
    payload = build_quick_replies(to, question, qr_buttons)
    json_log("wa_send_buttons", request_id=request_id, sessionId=session_id, to=to)
    return await _post_with_backoff(wa_base_url, token, payload, "wa_send", client)


async def _post_with_backoff(wa_base_url: str, token: str, payload: Dict[str, Any], metric_name: str, client: Optional[httpx.AsyncClient] = None) -> Tuple[int, Any]:
    backoff_series = [1, 2, 4]
    url = wa_base_url
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    close_client = False
    if client is None:
        # If WA_BASE_URL is not set in tests, short-circuit
        if not wa_base_url:
            return 200, {"mock": True}
        client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0))
        close_client = True
    try:
        for i, delay in enumerate(backoff_series):
            with time_histogram(metric_name):
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                except httpx.TimeoutException:
                    if i == len(backoff_series) - 1:
                        raise
                    await _sleep(delay)
                    continue
            if resp.status_code == 200:
                return 200, resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            if resp.status_code in (429, 500, 502, 503, 504):
                ra = resp.headers.get("Retry-After")
                wait = delay
                if ra and ra.isdigit():
                    wait = int(ra)
                if i == len(backoff_series) - 1:
                    return resp.status_code, resp.text
                await _sleep(wait)
                continue
            # other 4xx -> do not retry
            COUNTERS.setdefault("wa_send_fail", None)
            return resp.status_code, resp.text
        return 500, "max retries exceeded"
    finally:
        if close_client:
            await client.aclose()


async def _sleep(seconds: int):
    # small indirection for tests
    await httpx.AsyncClient()._transport.sleep(seconds)  # type: ignore[attr-defined]




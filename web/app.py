from __future__ import annotations

import os
import json
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse, Response, FileResponse
import uuid
from starlette.requests import Request
from starlette.routing import Route
from sqlalchemy import desc

from adapters.wa import verify_signature, normalize_inbound, send_text, send_buttons
from pic.contracts import PICMessage, PICContext
from pic.bus import PicBus
from agents import tier1, tier2
from telemetry.metrics import metrics_response, time_histogram, COUNTERS, json_log
from infra.dedupe import build_deduper
from infra.database import SessionLocal, Message, init_db


bus = PicBus(routes={"tier1": tier1.handle, "tier2": tier2.handle})
deduper = build_deduper()


def db_log(session_id: str, direction: str, text: str):
    db = SessionLocal()
    try:
        db.add(Message(session_id=session_id, direction=direction, text=text))
        db.commit()
    finally:
        db.close()


async def verify(request: Request) -> Response:
    with time_histogram("wa_inbound"):
        params = request.query_params
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge", "")
        if token and token == os.environ.get("WA_VERIFY_TOKEN"):
            return PlainTextResponse(challenge, status_code=200)
        return PlainTextResponse("forbidden", status_code=403)


async def inbound(request: Request) -> Response:
    raw = await request.body()
    sig = request.headers.get("X-Hub-Signature-256")
    app_secret = os.environ.get("APP_SECRET", "")
    if not verify_signature(app_secret, raw, sig):
        return PlainTextResponse("forbidden", status_code=403)

    event = json.loads(raw.decode("utf-8") or "{}")
    with time_histogram("wa_inbound"):
        payload = normalize_inbound(event)
        wa_id = payload.get("wa_message_id")
        if not deduper.add_if_new(f"wa:{wa_id}"):
            COUNTERS["dedupe_hits"].inc()
            json_log("dedupe_hit", wa_message_id=wa_id)
            return JSONResponse({"status": "ok"}, status_code=200)

        db_log(session_id=payload["sessionId"], direction="inbound", text=payload["text"])
        # Publish to bus: from wa-adapter to tier1
        pic = PICMessage(
            id=wa_id or "",
            from_="wa-adapter",
            to="tier1",
            context=PICContext(sessionId=payload["sessionId"], locale=payload.get("locale", "es-AR")),
            payload={"text": payload["text"]},
        )
        t1 = bus.route(pic)
        # escalate to tier2 when needed
        to_t2 = t1.intent not in {t1.intent.SALUDO, t1.intent.DESPEDIDA, t1.intent.UBICACION, t1.intent.POLITICAS} or (
            t1.confidence < 0.8 or t1.complexity_score >= 0.6
        )
        if to_t2:
            COUNTERS["t1_to_t2_escalations"].inc()
            pic.to = "tier2"
            pic.payload = {"t1": t1.model_dump()}
            t2 = bus.route(pic)
            return JSONResponse({"status": "ok", "t2": t2}, status_code=200)
        return JSONResponse({"status": "ok", "t1": t1.model_dump()}, status_code=200)


async def send(request: Request) -> Response:
    # Real outbound using WA Cloud API
    with time_histogram("wa_send"):
        body = await request.json()
        wa_base_url = os.environ.get("WA_BASE_URL", "")
        wa_token = os.environ.get("WA_TOKEN", "")
        to = body.get("to")
        session_id = body.get("sessionId", "")
        request_id = body.get("request_id", str(uuid.uuid4()))
        messages = body.get("messages", [])  # [{type: text|buttons, text:..., buttons:{id:title}}]
        results = []
        for msg in messages:
            text_to_send = ""
            if msg.get("type") == "text":
                text_to_send = msg.get("text", "")
                db_log(session_id=to, direction="outbound", text=text_to_send)
                code, res = await send_text(wa_base_url, wa_token, to, text_to_send, request_id=request_id, session_id=session_id)
            elif msg.get("type") == "buttons":
                text_to_send = msg.get("question", "")
                db_log(session_id=to, direction="outbound", text=text_to_send)
                code, res = await send_buttons(wa_base_url, wa_token, to, text_to_send, msg.get("buttons", {}), request_id=request_id, session_id=session_id)
            else:
                code, res = 400, {"error": "unknown message type"}
            results.append({"code": code, "response": res})
        return JSONResponse({"results": results}, status_code=200)


async def metrics(request: Request) -> Response:
    ctype, body = metrics_response()
    return Response(body, media_type=ctype)


async def get_messages(request: Request) -> Response:
    db = SessionLocal()
    try:
        messages = db.query(Message).order_by(desc(Message.timestamp)).limit(20).all()
        return JSONResponse([
            {
                "id": m.id,
                "timestamp": m.timestamp.isoformat(),
                "session_id": m.session_id,
                "direction": m.direction,
                "text": m.text,
            }
            for m in messages
        ])
    finally:
        db.close()


async def homepage(request: Request) -> Response:
    return FileResponse("web/templates/index.html")


routes = [
    Route("/", homepage),
    Route("/api/messages", get_messages),
    Route("/verify", verify, methods=["GET"]),
    Route("/inbound", inbound, methods=["POST"]),
    Route("/send", send, methods=["POST"]),
    Route("/metrics", metrics, methods=["GET"]),
]

app = Starlette(routes=routes, on_startup=[init_db])



from __future__ import annotations

import os
import json
import asyncio
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, PlainTextResponse, Response, FileResponse
import uuid
from starlette.requests import Request
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy import desc

from adapters.wa import verify_signature, normalize_inbound, send_text, send_buttons
from pic.contracts import PICMessage, PICContext
from agents.router import process_message
from telemetry.metrics import metrics_response, time_histogram, COUNTERS, json_log
from config.settings import settings
from infra.database import Message, init_db
from web.dependencies import get_deduper, SessionLocal, engine
from web.broadcaster import broadcaster

deduper = get_deduper()


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db = SessionLocal()
        request.state.db = db
        response = await call_next(request)
        db.close()
        return response


def db_log(db, session_id: str, direction: str, text: str) -> Message:
    msg = Message(session_id=session_id, direction=direction, text=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


async def verify(request: Request) -> Response:
    with time_histogram("wa_inbound"):
        params = request.query_params
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge", "")
        if token and token == settings.WA_VERIFY_TOKEN:
            return PlainTextResponse(challenge, status_code=200)
        return PlainTextResponse("forbidden", status_code=403)


async def inbound(request: Request) -> Response:
    raw = await request.body()
    sig = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(settings.APP_SECRET, raw, sig):
        return PlainTextResponse("forbidden", status_code=403)

    event = json.loads(raw.decode("utf-8") or "{}")
    with time_histogram("wa_inbound"):
        payload = normalize_inbound(event)
        wa_id = payload.get("wa_message_id")
        if not deduper.add_if_new(f"wa:{wa_id}"):
            COUNTERS["dedupe_hits"].inc()
            json_log("dedupe_hit", wa_message_id=wa_id)
            return JSONResponse({"status": "ok"}, status_code=200)

        msg = db_log(request.state.db, session_id=payload["sessionId"], direction="inbound", text=payload["text"])
        asyncio.create_task(broadcaster.broadcast(json.dumps({
            "id": msg.id, "timestamp": msg.timestamp.isoformat(), "session_id": msg.session_id,
            "direction": msg.direction, "text": msg.text
        })))

        pic = PICMessage(
            id=wa_id or "",
            from_="wa-adapter",
            to="tier1",
            context=PICContext(sessionId=payload["sessionId"], locale=payload.get("locale", "es-AR")),
            payload={"text": payload["text"]},
        )

        result = process_message(pic)
        return JSONResponse(result, status_code=200)


async def send(request: Request) -> Response:
    # Real outbound using WA Cloud API
    with time_histogram("wa_send"):
        body = await request.json()
        to = body.get("to")
        session_id = body.get("sessionId", "")
        request_id = body.get("request_id", str(uuid.uuid4()))
        messages = body.get("messages", [])  # [{type: text|buttons, text:..., buttons:{id:title}}]
        results = []
        for msg in messages:
            text_to_send = ""
            if msg.get("type") == "text":
                text_to_send = msg.get("text", "")
                db_msg = db_log(request.state.db, session_id=to, direction="outbound", text=text_to_send)
                asyncio.create_task(broadcaster.broadcast(json.dumps({
                    "id": db_msg.id, "timestamp": db_msg.timestamp.isoformat(), "session_id": db_msg.session_id,
                    "direction": db_msg.direction, "text": db_msg.text
                })))
                code, res = await send_text(settings.WA_BASE_URL, settings.WA_TOKEN, to, text_to_send, request_id=request_id, session_id=session_id)
            elif msg.get("type") == "buttons":
                text_to_send = msg.get("question", "")
                db_msg = db_log(request.state.db, session_id=to, direction="outbound", text=text_to_send)
                asyncio.create_task(broadcaster.broadcast(json.dumps({
                    "id": db_msg.id, "timestamp": db_msg.timestamp.isoformat(), "session_id": db_msg.session_id,
                    "direction": db_msg.direction, "text": db_msg.text
                })))
                code, res = await send_buttons(settings.WA_BASE_URL, settings.WA_TOKEN, to, text_to_send, msg.get("buttons", {}), request_id=request_id, session_id=session_id)
            else:
                code, res = 400, {"error": "unknown message type"}
            results.append({"code": code, "response": res})
        return JSONResponse({"results": results}, status_code=200)


async def metrics(request: Request) -> Response:
    ctype, body = metrics_response()
    return Response(body, media_type=ctype)


async def get_messages(request: Request) -> Response:
    db = request.state.db
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


async def homepage(request: Request) -> Response:
    return FileResponse("web/templates/index.html")


async def websocket_endpoint(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            # We just keep the connection open to send messages
            # A more advanced implementation might handle receiving messages here
            await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.remove(websocket)


def startup():
    init_db(engine)


middleware = [
    Middleware(DBSessionMiddleware)
]

routes = [
    Route("/", homepage),
    Route("/api/messages", get_messages),
    Route("/verify", verify, methods=["GET"]),
    Route("/inbound", inbound, methods=["POST"]),
    Route("/send", send, methods=["POST"]),
    Route("/metrics", metrics, methods=["GET"]),
    WebSocketRoute("/ws", websocket_endpoint),
]

app = Starlette(routes=routes, on_startup=[startup], middleware=middleware)



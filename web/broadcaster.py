import asyncio
from typing import List
from starlette.websockets import WebSocket

class Broadcast:
    def __init__(self):
        self._connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accepts and adds a new WebSocket connection.
        """
        await websocket.accept()
        self._connections.append(websocket)

    def remove(self, websocket: WebSocket):
        """
        Removes a WebSocket connection.
        """
        self._connections.remove(websocket)

    async def broadcast(self, message: str):
        """
        Broadcasts a message to all connected clients.
        """
        for connection in self._connections:
            await connection.send_text(message)

# Create a single instance of the broadcaster to be used in the application
broadcaster = Broadcast()

import asyncio
import logging

import websockets
from typing import Dict, Set

from starlette.websockets import WebSocket
logger = logging.getLogger('uvicorn.error')

class WebSocketManager:
    def __init__(self):
        print("WebSocketManager initialized")
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"Client connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        for topic in self.subscriptions.values():
            topic.discard(websocket)
        logger.info(f"Client disconnected: {websocket.client}")

    async def subscribe(self, websocket: WebSocket, topic: str):
        logger.info(f"Subscribing to topic: {topic}")
        self.subscriptions.setdefault(topic, set()).add(websocket)
        await websocket.send_json({"status": "subscribed", "topic": topic})

    async def unsubscribe(self, websocket: WebSocket, topic: str):
        logger.info(f"Unsubscribing from topic: {topic}")
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)
            await websocket.send_json({"status": "unsubscribed", "topic": topic})

    async def publish(self, topic: str, message: str):
        clients = self.subscriptions.get(topic, set())

        for client in clients:
            try:
                await client.send_json({
                    "topic": topic,
                    "message": message
                })
            except:
                self.disconnect(client)


import asyncio
import json
import logging

from typing import Dict, Set

from starlette.websockets import WebSocket

from path_value_matcher import matches_subset

logger = logging.getLogger('uvicorn.error')


class WebSocketManager:
    def __init__(self):
        logger.info("WebSocketManager initialized")
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected: {websocket.client}")

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

    def get_subscribed_clients(self, message):
        topic = None
        # find matching topic
        # probably better to just store the dict than the string.
        if type(message) is not dict:
            message_dict = json.loads(message)
        else:
            message_dict = message
        for key in self.subscriptions.keys():
            if matches_subset(json.loads(key),message_dict):
                topic = key
                break
        return self.subscriptions.get(topic, set())

    async def publish(self, message: str, clients: Set[WebSocket]):

        for client in clients:
            try:
                logger.info(f"Publishing message to {client.client}")
                await client.send_json({
                    "message": message
                })
            except Exception:
                logger.error(f"Error sending message to {client.client}")
                self.disconnect(client)

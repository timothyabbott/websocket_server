import asyncio
import json
import logging

from typing import Dict, Set

from starlette.websockets import WebSocket

from example_messages.path_value_matcher import create_pattern_matcher, matches_value

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
        # store the matching pattern rather have to calculate it each time?
        for key in self.subscriptions.keys():
            message_dict = json.loads(message)
            *pattern, value = key.split(",")
            match_pattern = create_pattern_matcher(*pattern)

            if matches_value(message_dict, match_pattern, value):
                topic = key
                break
        return self.subscriptions.get(topic, set())

    async def publish(self, message: str):

        clients = self.get_subscribed_clients(message)

        for client in clients:
            try:
                logger.info(f"Publishing message to {client.client}")
                await client.send_json({
                    "message": message
                })
            except:
                logger.error(f"Error sending message to {client.client}")
                self.disconnect(client)

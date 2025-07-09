import json

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from websocket_server import WebSocketManager
import logging
logger = logging.getLogger('uvicorn.error')

app = FastAPI()
manager = WebSocketManager()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("New connection")
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            action = data.get("action")
            topic = data.get("topic")
            message = data.get("message")
            logger.info(f"Received message: {message}")
            if action == "subscribe" and topic:
                # one socket can subscribe to multiple topics(which can be any string)
                await manager.subscribe(websocket, topic)
            elif action == "unsubscribe" and topic:
                await manager.unsubscribe(websocket, topic)
            elif action == "publish" and message:

                # here we want to action the message, but only "reply" based on the topic and content in the message.

                await manager.publish(message)
            else:
                logger.error(f"Invalid message: {raw_data}")
                await websocket.send_json({"error": "Invalid message format"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
import json

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from websocket_server import WebSocketManager

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

            if action == "subscribe" and topic:
                await manager.subscribe(websocket, topic)
            elif action == "unsubscribe" and topic:
                await manager.unsubscribe(websocket, topic)
            elif action == "publish" and topic and message:
                await manager.publish(topic, message)
            else:
                await websocket.send_json({"error": "Invalid message format"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
import json

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from message_config import MessageConfig
from message_router import MessageRouter
from websocket_server import WebSocketManager
import logging
logger = logging.getLogger('uvicorn.error')

app = FastAPI()
manager = WebSocketManager()
message_config = MessageConfig(manager)
router = MessageRouter(message_config)



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("New connection")
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            logger.info(f"Received message: {raw_data}")
            await router.route_message(websocket, raw_data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
from starlette.websockets import WebSocket
import json
from pydantic import ValidationError
import logging

logger = logging.getLogger('uvicorn.error')


class MessageRouter:
    def __init__(self, message_config):
        self.config = message_config

    async def route_message(self, websocket: WebSocket, raw_data: str) -> None:
        try:
            logger.info("routing message")
            data = json.loads(raw_data)
            action = data.get("action")

            if action not in self.config.handlers:
                logger.error(f"Unknown action: {action}")
                await websocket.send_json({
                    "error": f"Unknown action: {action}"

                })
                return

            handler_config = self.config.handlers[action]

            try:
                # Validate using Pydantic model
                validated_data = handler_config.validation_model(**data)
                await handler_config.handler_function(websocket, validated_data)
            except ValidationError as e:
                logger.error(f"Validation error: {e.errors()}")
                await websocket.send_json({
                    "error": "Validation error",
                    "details": e.errors()
                })

        except json.JSONDecodeError:
            await websocket.send_json({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send_json({"error": "Internal server error"})
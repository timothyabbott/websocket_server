import json
from starlette.websockets import WebSocket

from message_models import HandlerConfig, SubscribePayload, PublishPayload, UnsubscribePayload


class MessageConfig:
    def __init__(self, manager):
        self.manager = manager
        self.handlers = {
            # in mo-studio, these could be register deregister and event.
            "subscribe": HandlerConfig(
                handler_function=self._handle_subscribe,
                validation_model=SubscribePayload
            ),
            "publish": HandlerConfig(
                handler_function=self._handle_publish,
                validation_model=PublishPayload
            ),
            "unsubscribe": HandlerConfig(
                handler_function=self._handle_unsubscribe,
                validation_model=UnsubscribePayload
            )
        }

    async def _handle_subscribe(self, websocket: WebSocket, data: SubscribePayload) -> None:
        await self.manager.subscribe(websocket, data.topic)

    async def _handle_publish(self, websocket: WebSocket, data: PublishPayload) -> None:
        # in mo-studio, there could be an event handler here.
        message = json.loads(data.message)
        clients = self.manager.get_subscribed_clients(message)
        await self.manager.publish(json.dumps(message), clients)

    async def _handle_unsubscribe(self, websocket: WebSocket, data: UnsubscribePayload) -> None:
        await self.manager.unsubscribe(websocket, data.topic)

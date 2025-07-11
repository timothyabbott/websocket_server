# message_models.py
from typing import Callable, Dict, Any
from typing_extensions import Annotated
from pydantic import BaseModel, Field, ConfigDict

class HandlerConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    handler_function: Callable
    validation_model: type[BaseModel]

class SceneData(BaseModel):
    sceneId: str
    state: str | None = None
    percent: int | None = None

class MessageBody(BaseModel):
    event: str
    data: SceneData | None = None

class BaseMessage(BaseModel):
    type: str
    body: MessageBody

class RegisterMessage(BaseMessage):
    type: Annotated[str, Field(pattern="^register$")]
    mosysId: str

class DeregisterMessage(BaseMessage):
    type: Annotated[str, Field(pattern="^deregister$")]
    mosysId: str

class EventMessage(BaseMessage):
    type: Annotated[str, Field(pattern="^event$")]
    Id: str

# WebSocket message models
class SubscribePayload(BaseModel):
    action: Annotated[str, Field(pattern="^subscribe$")]
    topic: str

class PublishPayload(BaseModel):
    action: Annotated[str, Field(pattern="^publish$")]
    message: BaseMessage | str

class UnsubscribePayload(BaseModel):
    action: Annotated[str, Field(pattern="^unsubscribe$")]
    topic: str
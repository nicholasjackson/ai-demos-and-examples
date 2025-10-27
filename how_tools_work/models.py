"""
OpenAI API compatible data models.
"""

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatCompletionMessage(BaseModel):
    """A single message in a chat conversation."""

    role: Literal["system", "user", "assistant", "function"]
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """Request format for /v1/chat/completions endpoint."""

    model: str
    messages: List[ChatCompletionMessage]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    n: Optional[int] = 1
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, int]] = None
    user: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    """A single completion choice."""

    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[Literal["stop", "length", "function_call"]] = None


class Usage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Response format for /v1/chat/completions endpoint."""

    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class StreamChoice(BaseModel):
    """A single streaming choice."""

    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class StreamResponse(BaseModel):
    """Streaming response chunk."""

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]


class Model(BaseModel):
    """Represents a single model in the OpenAI API format."""

    id: str
    object: Literal["model"] = "model"
    created: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
    )
    owned_by: str = "custom"


class ModelList(BaseModel):
    """Response for the /v1/models endpoint."""

    object: Literal["list"] = "list"
    data: List[Model]

from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
from ollama import Client, ChatResponse
import uuid
import json
import asyncio
import os

from models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionMessage,
    Usage,
    Model,
    ModelList,
    StreamChoice,
    StreamResponse,
)

app = FastAPI(title="Mock OpenAI API", version="1.0.0")

# Add CORS middleware for Chat-UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_ollama_client() -> Client:
    """Initialize and return the Ollama client."""

    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    return Client(host=ollama_host)


@app.get("/")
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Mock OpenAI API is running"}


@app.get("/v1/models")
def list_models():
    """List available models."""

    # hit ollama to get models
    list_models = get_ollama_client().list()
    print("Ollama models:", list_models)

    data = []
    for m in list_models.models:
        if m.model:
            data.append(Model(id=m.model, owned_by="custom"))

    return ModelList(data=data)


async def generate_stream(
    completion_id: str, model: str, content: str
) -> AsyncGenerator[str, None]:
    """Generate streaming response chunks."""
    # Send initial chunk with role
    yield f"data: {json.dumps(StreamResponse(id=completion_id, created=int(datetime.now().timestamp()), model=model, choices=[StreamChoice(index=0, delta={'role': 'assistant'}, finish_reason=None)]).model_dump())}\n\n"

    # Stream content word by word
    words = content.split()
    for i, word in enumerate(words):
        chunk = StreamResponse(
            id=completion_id,
            created=int(datetime.now().timestamp()),
            model=model,
            choices=[
                StreamChoice(
                    index=0,
                    delta={"content": word + (" " if i < len(words) - 1 else "")},
                    finish_reason=None,
                )
            ],
        )
        yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        await asyncio.sleep(0.05)  # Simulate streaming delay

    # Send final chunk
    final_chunk = StreamResponse(
        id=completion_id,
        created=int(datetime.now().timestamp()),
        model=model,
        choices=[StreamChoice(index=0, delta={}, finish_reason="stop")],
    )
    yield f"data: {json.dumps(final_chunk.model_dump())}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    """Handle chat completion requests (streaming and non-streaming)."""
    # Get the last user message
    user_message = next(
        (msg.content for msg in reversed(req.messages) if msg.role == "user"), "Hello"
    )

    # Send to ollama chat endpoint
    resp = get_ollama_client().chat(
        model=req.model,
        messages=[{"role": "user", "content": user_message}],
    )
    response_content = resp.message.content if resp.message.content else ""

    print("Ollama chat response:", resp)

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    # Handle streaming
    if req.stream:
        return StreamingResponse(
            generate_stream(completion_id, req.model, response_content),
            media_type="text/event-stream",
        )

    # Handle non-streaming
    return ChatCompletionResponse(
        id=completion_id,
        object="chat.completion",
        created=int(datetime.now().timestamp()),
        model=req.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatCompletionMessage(role="assistant", content="ok"),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=len(user_message.split()),
            completion_tokens=len(response_content),
            total_tokens=len(user_message.split()) + len(response_content),
        ),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

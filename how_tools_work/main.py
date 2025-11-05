from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
from ollama import Client
import uuid
import json
import asyncio
import os
from pydantic import BaseModel, ValidationError

from weather import get_weather

from models import (
    ChatCompletionRequest,
    Model,
    ModelList,
    StreamChoice,
    StreamResponse,
)


class ToolCall(BaseModel):
    tool: str
    parameters: dict


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


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    """Handle chat completion requests (streaming and non-streaming)."""

    # Get the last user message
    user_message = next(
        (msg.content for msg in reversed(req.messages) if msg.role == "user"), "Hello"
    )

    # Load the system prompt from file
    with open("./prompt.md", "r") as f:
        system_prompt = f.read()
        print("Loaded system prompt from file.", system_prompt)

    # Send to ollama chat endpoint
    resp = get_ollama_client().generate(
        model=req.model, system=system_prompt, prompt=user_message
    )

    # Print the response from ollama
    response_data = resp.response
    print("Ollama chat response:", response_data)

    # If the response contains a tool call, handle it
    try:
        tool_call = ToolCall.model_validate_json(response_data)
        if tool_call.tool == "weather":
            location = tool_call.parameters.get("city", "unknown")

            response_data = get_weather(location)

            print(
                f"Tool call 'weather' executed for location: {location}, result: {response_data}"
            )

    except ValidationError as e:
        # Not a tool call, return as normal chat response
        print("Response is not a tool call:")

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    # Handle streaming
    return StreamingResponse(
        generate_stream(completion_id, req.model, response_data),
        media_type="text/event-stream",
    )


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

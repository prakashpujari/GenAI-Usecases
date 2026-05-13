import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from chatbot import TerminalChatbot

_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

bot = TerminalChatbot()


class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message cannot be empty")
        if len(v) > 32_000:
            raise ValueError("message exceeds 32,000 character limit")
        return v


@app.get("/api/status")
def status():
    return {"provider": bot.provider, "model": bot.model}


@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        reply, usage = bot.send(req.message)
    except Exception:
        raise HTTPException(status_code=502, detail="AI provider request failed")

    if bot.provider == "anthropic":
        usage_dict = {
            "input": usage.input_tokens,
            "output": usage.output_tokens,
            "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
            "cache_write": getattr(usage, "cache_creation_input_tokens", 0) or 0,
        }
    else:
        usage_dict = {
            "input": usage.prompt_tokens,
            "output": usage.completion_tokens,
        }
    return {"reply": reply, "usage": usage_dict, "turn_count": bot.turn_count}


@app.post("/api/reset")
def reset():
    bot.reset()
    return {"message": "Conversation reset"}

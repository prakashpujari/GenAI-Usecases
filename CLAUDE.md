# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A multi-turn AI chatbot with two interfaces: a React/Vite web UI and a terminal CLI. The Python backend uses Anthropic (Claude) as the primary provider with automatic OpenAI fallback.

## Repository Layout

```
Claude-Anthropic/
├── docs/                          # Reference docs (certification PDF)
└── claude_chatbot/
    ├── backend/                   # Python backend
    │   ├── chatbot.py             # TerminalChatbot class — core logic, provider selection
    │   ├── api.py                 # FastAPI server exposing /api/chat, /api/status, /api/reset
    │   └── main.py                # Terminal CLI entry point
    ├── frontend/                  # React + Vite UI
    │   └── src/
    │       ├── App.jsx            # Single-component UI (all state, fetch calls, rendering)
    │       └── App.css
    ├── requirements.txt
    └── .env.example
```

## Development Commands

### Backend

```powershell
# Install dependencies (run from claude_chatbot/)
pip install -r requirements.txt

# Start the API server (run from claude_chatbot/backend/)
uvicorn api:app --reload --port 8000

# Run terminal CLI (run from claude_chatbot/backend/)
python main.py
```

### Frontend

```powershell
# Install dependencies (run from claude_chatbot/frontend/)
npm install

# Start dev server (proxies /api/* to localhost:8000)
npm run dev

# Production build
npm run build
```

### Environment setup

Copy `claude_chatbot/.env.example` to `claude_chatbot/.env` and set at least one key:

```
ANTHROPIC_API_KEY=sk-ant-...   # preferred
OPENAI_API_KEY=sk-...          # fallback if Anthropic key is absent
```

Or export them in your shell before starting the server.

## Architecture

### Provider selection (`chatbot.py`)

`TerminalChatbot.__init__` checks environment variables at startup: `ANTHROPIC_API_KEY` takes priority; `OPENAI_API_KEY` is the fallback. The selected provider and model are stored as instance attributes (`bot.provider`, `bot.model`) and exposed via `GET /api/status`.

### Prompt caching (Anthropic only)

The system prompt is wrapped with `cache_control: ephemeral`. Turn 1 writes it to Anthropic's cache (`cache_creation_input_tokens`); subsequent turns read from cache (`cache_read_input_tokens`), reducing cost and latency. This is visible in the token usage footer of each response.

### API ↔ Frontend contract

The Vite dev server proxies all `/api/*` requests to `http://localhost:8000` (configured in `vite.config.js`). The three endpoints are:

| Endpoint | Purpose |
|---|---|
| `GET /api/status` | Returns `{provider, model}` — fetched once on UI load |
| `POST /api/chat` | `{message}` → `{reply, usage, turn_count}` |
| `POST /api/reset` | Clears server-side conversation history |

Usage shape differs by provider: Anthropic responses include `cache_read` and `cache_write` fields; OpenAI responses only have `input` and `output`. `api.py` normalizes both into a flat dict before sending to the frontend.

### Single backend instance

`api.py` instantiates one global `TerminalChatbot` at module load time. Conversation history lives in memory on that instance — a server restart clears it.

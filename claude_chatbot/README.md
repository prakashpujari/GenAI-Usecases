# Joshitha's chatbot

A multi-turn AI chatbot with a React UI and terminal CLI, powered by Claude (Anthropic) with automatic OpenAI fallback.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                           │
│                   http://localhost:5173                         │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │               React Frontend  (Vite)                    │   │
│   │                                                         │   │
│   │   ┌──────────┐   ┌────────────────┐   ┌─────────────┐  │   │
│   │   │  Header  │   │ Messages Area  │   │  Input Bar  │  │   │
│   │   │ provider │   │ user bubbles   │   │  textarea   │  │   │
│   │   │  model   │   │  ai bubbles    │   │ send button │  │   │
│   │   │  reset   │   │ token usage    │   │             │  │   │
│   │   └──────────┘   └────────────────┘   └─────────────┘  │   │
│   └───────────────────────┬─────────────────────────────────┘   │
│                           │  /api/*  (proxied by Vite)          │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼ HTTP REST
┌───────────────────────────────────────────────────────────────┐
│              FastAPI Backend  (Uvicorn, port 8000)            │
│                                                               │
│   GET  /api/status   →  provider + model info                 │
│   POST /api/chat     →  send message, get reply + usage       │
│   POST /api/reset    →  clear conversation history            │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                  TerminalChatbot                      │   │
│   │                                                       │   │
│   │   • Maintains message history (multi-turn)            │   │
│   │   • Prompt caching on system prompt (Anthropic)       │   │
│   │   • Automatic provider fallback logic                 │   │
│   └──────────────┬────────────────────┬───────────────────┘   │
└──────────────────┼────────────────────┼───────────────────────┘
                   │                    │
       ANTHROPIC_API_KEY           OPENAI_API_KEY
         (primary)                  (fallback)
                   │                    │
                   ▼                    ▼
        ┌──────────────────┐  ┌──────────────────┐
        │  Anthropic API   │  │   OpenAI API     │
        │ claude-sonnet-4-6│  │    gpt-4o        │
        └──────────────────┘  └──────────────────┘


  Alternate path — Terminal CLI:
  ┌────────────────────────────────────┐
  │  python main.py  (stdin / stdout)  │
  │  same TerminalChatbot core         │
  └────────────────────────────────────┘
```

---

## UI Preview

### React Web UI (http://localhost:5173)

```
+--------------------------------------------------------------+
|  Joshitha's chatbot   [openai] gpt-4o           [  Reset  ] |
+--------------------------------------------------------------+
|                                                              |
|                                                              |
|          Send a message to start chatting.                   |
|                                                              |
|                                                              |
|        +----------------------------------------------+      |
|        |  Hello! I can help you with:                 |      |
|        |   - Writing and editing                      |      |
|        |   - Coding and debugging                     |      |
|        |   - Math and analysis                        |      |
|        |   - General knowledge questions              |      |
|        |  What would you like to explore?             |      |
|        +----------------------------------------------+      |
|        in: 78  out: 93  --  turn 1                          |
|                                                              |
|                   [What is 12 * 8?               ]          |
|                                                              |
|        +----------------------------------------------+      |
|        |  12 * 8 = 96                                |      |
|        +----------------------------------------------+      |
|        in: 142  out: 9  --  turn 2                          |
|                                                              |
|                   [Explain it step by step       ]          |
|                                                              |
|        +----------------------------------------------+      |
|        |  Sure! 12 * 8 means adding 12 eight times:  |      |
|        |  12 + 12 = 24  (x2)                         |      |
|        |  24 + 24 = 48  (x4)                         |      |
|        |  48 + 48 = 96  (x8)                         |      |
|        +----------------------------------------------+      |
|        in: 187  out: 55  --  turn 3                         |
|                                                              |
+--------------------------------------------------------------+
| Type a message... (Enter to send, Shift+Enter for newline)   |
|                                               [   Send   ]   |
+--------------------------------------------------------------+
```

**UI elements explained:**

| Element | Location | Description |
|---------|----------|-------------|
| `[openai]` badge | Top-left | Active provider — green teal pill |
| `gpt-4o` | Header | Active model name |
| `[Reset]` | Top-right | Clears conversation history |
| Right-aligned bubbles | Messages area | Your messages (teal gradient) |
| Left-aligned bubbles | Messages area | AI replies (warm cream) |
| `in: / out:` footer | Below AI bubble | Token usage per reply |
| Loading dots | Messages area | Three animated dots while AI is thinking |

---

### Terminal CLI

```
+------------------------------------------+
|          Joshitha's chatbot              |
|   Provider: openai  Model: gpt-4o        |
|   Type /help for available commands      |
+------------------------------------------+

You: Hello, what can you help me with?

Joshitha's chatbot: I can assist you with a wide range of tasks including
coding, writing, math, analysis, and general knowledge questions.

[turn 1 | in:78  out:64]

You: Write a Python function to check if a number is prime

Joshitha's chatbot: def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

[turn 2 | in:156  out:58]

You: reset
-- Conversation reset --

You: quit
Goodbye!
```

---

## Example Conversations

### 1. General Knowledge

**You:** What is the difference between RAM and ROM?

**AI:** RAM (Random Access Memory) is temporary storage — it holds data the
computer is actively using and is cleared when powered off. ROM (Read-Only
Memory) is permanent storage that retains data even without power, typically
used to store firmware like the BIOS.

---

### 2. Coding Help

**You:** Write a Python function to reverse a string.

**AI:**
```python
def reverse_string(s: str) -> str:
    return s[::-1]

# Example
print(reverse_string("hello"))  # "olleh"
```

**You:** Now make it handle None input safely.

**AI:**
```python
def reverse_string(s: str | None) -> str:
    if s is None:
        return ""
    return s[::-1]
```

> Multi-turn context: the AI remembered your first function and improved it.

---

### 3. Writing Help

**You:** Write a one-line bio for a software engineer named Alex.

**AI:** Alex is a software engineer passionate about building scalable systems
and turning complex problems into elegant solutions.

---

### 4. Math & Analysis

**You:** I have 3 apples and buy 2 bags of 6 apples each. How many do I have?

**AI:** You start with 3 apples, then buy 2 × 6 = 12 more. Total: 3 + 12 = **15 apples**.

---

### 5. Reset and Start Fresh

**You:** reset

```
-- Conversation reset --
```

The AI now has no memory of previous messages — useful when switching topics.

---

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| API Key | OpenAI or Anthropic | — |

---

## Step-by-Step Setup

### Step 1 — Clone / open the project

```
claude_chatbot/
  backend/            ← Python backend
    chatbot.py        ← core AI logic
    api.py            ← FastAPI backend
    main.py           ← terminal CLI
  frontend/           ← React app
    src/
      App.jsx
      App.css
      main.jsx
    package.json
    vite.config.js
    index.html
  requirements.txt    ← Python deps
  .env.example        ← API key template
  .gitignore
```

### Step 2 — Set your API key

Copy `.env.example` to `.env` and fill in your key:

```
ANTHROPIC_API_KEY=sk-ant-...    ← primary (Claude)
OPENAI_API_KEY=sk-...           ← fallback (GPT-4o)
```

**Priority rule:** If `ANTHROPIC_API_KEY` is set, Claude is used. If only `OPENAI_API_KEY` is set, GPT-4o is used as fallback.

Or set it directly in your terminal session:

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

```bash
# macOS / Linux
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Step 3 — Install Python dependencies

```powershell
cd claude_chatbot
pip install -r requirements.txt
```

### Step 4 — Install frontend dependencies

```powershell
cd claude_chatbot/frontend
npm install
```

### Step 5 — Start the backend

Open a terminal in `claude_chatbot/backend/`:

```powershell
cd claude_chatbot/backend
uvicorn api:app --reload --port 8000
```

Verify it's running: http://localhost:8000/api/status

Expected response:
```json
{ "provider": "openai", "model": "gpt-4o" }
```

### Step 6 — Start the frontend

Open a second terminal in `claude_chatbot/frontend/`:

```powershell
npm run dev
```

Open your browser at **http://localhost:5173**

Installed packages:

| Package | Purpose |
|---------|---------|
| `anthropic` | Claude API client |
| `openai` | OpenAI fallback client |
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |

---

## Using the React UI

| Element | Description |
|---------|-------------|
| Header badge | Shows active provider (anthropic / openai) |
| Header model | Shows active model name |
| Reset button | Clears conversation history |
| Message bubbles | Purple = you, Gray = AI |
| Token usage | Shown below each AI reply (input · output · cache) |
| Enter | Send message |
| Shift + Enter | New line in input |

---

## Using the Terminal CLI

```powershell
cd claude_chatbot/backend
python main.py
```

| Command | Action |
|---------|--------|
| `reset` | Clear conversation and start fresh |
| `/help` | Show available commands |
| `quit` | Exit the chatbot |
| `exit` | Exit the chatbot |

---

## API Reference

### `GET /api/status`
Returns the active provider and model.

```json
{ "provider": "openai", "model": "gpt-4o" }
```

### `POST /api/chat`
Send a message and receive a reply.

**Request:**
```json
{ "message": "Hello, what can you do?" }
```

**Response:**
```json
{
  "reply": "I can help with coding, writing...",
  "usage": { "input": 78, "output": 93 },
  "turn_count": 1
}
```

Anthropic usage includes additional cache fields:
```json
{
  "input": 78, "output": 93,
  "cache_read": 512, "cache_write": 0
}
```

### `POST /api/reset`
Clears the conversation history.

```json
{ "message": "Conversation reset" }
```

---

## How Prompt Caching Works (Anthropic only)

When using Claude, the system prompt is marked with `cache_control: ephemeral`. On the first turn Anthropic writes the prompt to cache (`cache_write` tokens). All subsequent turns read from cache (`cache_read` tokens) instead of re-processing the system prompt, reducing cost and latency.

```
Turn 1:  cache_write: 42  (system prompt written to cache)
Turn 2:  cache_read:  42  (system prompt served from cache)
Turn 3:  cache_read:  42  (same)
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No API key found` | Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in your shell |
| `Cannot connect to backend` | Make sure `uvicorn` is running on port 8000 |
| `CORS error in browser` | Backend must be on port 8000; do not change `vite.config.js` proxy |
| `ModuleNotFoundError: fastapi` | Run `pip install -r requirements.txt` |
| `npm: command not found` | Install Node.js from https://nodejs.org |

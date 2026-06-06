# LangGraph RAG Agent

> LangGraph + OpenAI + FAISS + PostgreSQL — production-grade RAG & Tool-Calling agent with a React/TypeScript UI.

---

## Architecture

```mermaid
graph TB
    subgraph Browser["🌐  Browser — localhost:5173"]
        direction TB
        subgraph ReactApp["React 18 + TypeScript + Tailwind CSS"]
            SB["Sidebar\nhealth · session stats · dark mode"]
            CM["ChatMessages\nuser & assistant bubbles · auto-scroll"]
            CI["ChatInput\ntextarea · suggestion chips"]
            IP["InspectorPanel\nPipeline · Documents · SQL tabs"]
        end
        ZS[("Zustand Store\nmessages · health · selectedId · isLoading")]
        AX["Axios Client\nproxy /api → localhost:8000"]
        ReactApp <--> ZS
        ZS <--> AX
    end

    subgraph Backend["⚙️  Backend — localhost:8000 (FastAPI + uvicorn)"]
        direction TB
        subgraph APILayer["API Layer"]
            QR["POST /api/query\nQueryRequest → QueryResponse"]
            HR["GET /api/health\nliveness + db status"]
        end

        subgraph LangGraph["LangGraph Workflow  (StateGraph)"]
            direction LR
            ST(["START"]) --> RO
            RO["🔀 router\ngpt-4o classifies\nrag / sql / both"]
            RE["🔍 retrieve\nFAISS semantic\ntop-3 chunks"]
            SN["🗄️ sql_node\ngpt-4o generates SQL\nQuerySQLDatabaseTool executes"]
            LN["🤖 llm_node\ngpt-4o merges context\n→ final answer"]
            EN(["END"])

            RO -->|"rag or both"| RE
            RO -->|"sql"| SN
            RE -->|"both"| SN
            RE -->|"rag"| LN
            SN --> LN
            LN --> EN
        end

        APILayer --> LangGraph
    end

    subgraph DataStores["💾  Data Stores"]
        FAISS[("FAISS\nIn-Memory\nVector Store\n6 sample docs")]
        PG[("PostgreSQL 17\nlocalhost:5432/postgres\nemployees table\nAlice · Bob · Carol")]
    end

    subgraph OpenAI["☁️  OpenAI API"]
        EMB["text-embedding-3-small\nDoc & query embeddings"]
        GPT["gpt-4o\nrouting · SQL gen · final answer"]
    end

    AX <-->|"HTTP/JSON"| APILayer
    RE <-->|"embed + search"| FAISS
    FAISS <-->|"embed docs at startup"| EMB
    RE <-->|"embed query"| EMB
    SN <-->|"execute SQL"| PG
    RO & SN & LN <-->|"chat completions"| GPT
```

### LangGraph routing logic

| Query type | Graph path |
|---|---|
| `rag` | router → retrieve → llm |
| `sql` | router → sql_node → llm |
| `both` | router → retrieve → sql_node → llm |

### Layer summary

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | React 18 + Zustand + Axios | Chat UI, inspector panel, health display |
| **API** | FastAPI + uvicorn | Request validation, graph invocation |
| **Orchestration** | LangGraph `StateGraph` | Stateful multi-node conditional workflow |
| **Vector search** | FAISS + OpenAI embeddings | Semantic document retrieval |
| **Structured data** | psycopg2 + LangChain SQL tool | Natural-language → SQL → results |
| **LLM** | OpenAI gpt-4o | Routing, SQL generation, final answer synthesis |

---

## Project Structure

```
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app + lifespan startup
│       ├── config.py            # pydantic-settings (reads .env)
│       ├── logging_config.py    # structured stdout logging
│       ├── api/
│       │   ├── schemas.py       # Pydantic request/response models
│       │   └── routes/
│       │       ├── health.py    # GET /api/health
│       │       └── query.py     # POST /api/query
│       ├── graph/
│       │   ├── builder.py       # LangGraph StateGraph factory
│       │   ├── state.py         # AgentState TypedDict
│       │   └── nodes/
│       │       ├── router.py    # classifies query → rag/sql/both
│       │       ├── retrieve.py  # FAISS semantic search
│       │       ├── sql_node.py  # SQL generation + execution
│       │       └── llm_node.py  # final answer synthesis
│       └── tools/
│           ├── vector_store.py  # builds FAISS retriever
│           └── sql_tool.py      # PostgreSQL setup + SQL tool
└── frontend/
    ├── src/
    │   ├── App.tsx              # 3-column layout
    │   ├── components/          # Sidebar, Chat, Inspector, etc.
    │   ├── services/api.ts      # Axios HTTP client
    │   ├── store/agentStore.ts  # Zustand global state
    │   └── types/index.ts       # mirrors backend Pydantic schemas
    ├── vite.config.ts           # /api proxy → localhost:8000
    └── tailwind.config.js       # dark mode + custom brand colours
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 17 running on `localhost:5432`
- OpenAI API key

### Backend

```bash
cd backend
cp .env.example .env          # add your OPENAI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # opens localhost:5173
```

### Environment variables (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required |
| `OPENAI_MODEL` | `gpt-4o` | Chat model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `POSTGRES_DSN` | `postgresql://postgres:postgres@localhost:5432/postgres` | Database DSN |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

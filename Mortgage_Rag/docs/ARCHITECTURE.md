# 🏗️ SecureMortgageAI - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                         (Streamlit Web Application)                          │
│                                                                              │
│  ┌──────────────┐                                    ┌──────────────────┐   │
│  │   Sidebar    │                                    │   Main Chat      │   │
│  │  📁 Upload   │                                    │   💬 Interface   │   │
│  │  🛡️ Security │                                    │   📚 Sources     │   │
│  └──────────────┘                                    └──────────────────┘   │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INPUT PROCESSING LAYER                               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                     INPUT GUARDRAILS                                │    │
│  │  ✓ Length validation (3-500 chars)                                 │    │
│  │  ✓ Prompt injection detection                                      │    │
│  │  ✓ Inappropriate content filtering                                 │    │
│  │  ✓ Topic relevance check                                           │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                      PII DETECTION                                  │    │
│  │  Regex patterns for 8 types:                                       │    │
│  │  • SSN    • DOB    • Email   • Phone                               │    │
│  │  • Routing • Account • EIN   • Address                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENT PROCESSING LAYER                             │
│                                                                              │
│  ┌──────────────┐          ┌──────────────┐          ┌──────────────┐      │
│  │ PDF Extract  │   →      │ Text Split   │   →      │ PII Redact   │      │
│  │  (PyPDF)     │          │ (LangChain)  │          │ (src/pii.py) │      │
│  └──────────────┘          └──────────────┘          └──────────────┘      │
│       ↓                         ↓                          ↓                │
│   Extract text           Split into chunks          Replace PII with        │
│   from each page         (500 chars,50 overlap)     [TYPE_REDACTED]        │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EMBEDDING & STORAGE LAYER                             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    OpenAI Embeddings API                            │    │
│  │                  (text-embedding-ada-002)                           │    │
│  │  Converts text chunks → 1536-dimensional vectors                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    FAISS Vector Store                               │    │
│  │  • Stores embeddings in memory                                     │    │
│  │  • Fast similarity search (L2 distance)                            │    │
│  │  • Metadata: source file, chunk number                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RETRIEVAL LAYER                                     │
│                                                                              │
│  User Query → Embed Query → Vector Search → Relevance Filter               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  FAISS Similarity Search (k=4)                                      │    │
│  │  Returns: [(doc, score), (doc, score), ...]                        │    │
│  │  Score: L2 distance (lower = more similar)                         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Relevance Threshold Filter (score < 1.5)                          │    │
│  │  Removes low-quality results                                       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       OUTPUT PROCESSING LAYER                                │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                     OUTPUT GUARDRAILS                               │    │
│  │  ✓ Check retrieved docs for PII leaks                              │    │
│  │  ✓ Sanitize results (remove script tags, XSS)                      │    │
│  │  ✓ Double-check PII redaction                                      │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LLM GENERATION LAYER                                 │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    OpenAI Chat Completions API                      │    │
│  │                        (GPT-4o-mini)                                │    │
│  │                                                                     │    │
│  │  Input:                                                             │    │
│  │  • System prompt (roles & instructions)                            │    │
│  │  • User query                                                       │    │
│  │  • Context from sanitized search results                           │    │
│  │                                                                     │    │
│  │  Output:                                                            │    │
│  │  • Natural language summary                                        │    │
│  │  • Temperature: 0.3 (focused, less creative)                       │    │
│  │  • Max tokens: 500                                                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │               FINAL PII REDACTION (Critical!)                       │    │
│  │  Apply redact_pii() to LLM response                                │    │
│  │  Catches any hallucinated PII in generated text                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RESPONSE DISPLAY                                   │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Chat Interface displays:                                           │    │
│  │  • AI-generated answer (PII-safe)                                  │    │
│  │  • Source citations with relevance scores                          │    │
│  │  • Document names and chunk numbers                                │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
┌─────────┐
│  User   │
│ Uploads │
│   PDF   │
└────┬────┘
     │
     ▼
┌─────────────────┐
│  Extract Text   │ ──────► [Raw text with PII]
└────┬────────────┘
     │
     ▼
┌─────────────────┐         ┌──────────────┐
│  Detect PII     │ ──────► │ PiiMatch[]   │
└────┬────────────┘         │ - SSN: ***   │
     │                      │ - Email: *** │
     │                      └──────────────┘
     ▼
┌─────────────────┐
│  Redact PII     │ ──────► [Text with [SSN_REDACTED]]
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Chunk Text     │ ──────► [500-char chunks]
└────┬────────────┘
     │
     ▼
┌─────────────────────┐
│  Create Embeddings  │ ──────► [1536-dim vectors]
└────┬────────────────┘
     │
     ▼
┌─────────────────┐
│  Store in FAISS │
└────┬────────────┘
     │
     │  ┌─────────┐
     │  │  User   │
     │  │ Enters  │
     │  │  Query  │
     │  └────┬────┘
     │       │
     │       ▼
     │  ┌──────────────────┐
     │  │ Input Guardrails │ ──X──► [Block if malicious]
     │  └────┬─────────────┘
     │       │ [Pass]
     │       ▼
     ├─► ┌──────────────────┐
         │  Embed Query     │ ──────► [Query vector]
         └────┬─────────────┘
              │
              ▼
         ┌──────────────────┐
         │ Similarity Search│ ──────► [(doc, 0.3), (doc, 0.5), ...]
         └────┬─────────────┘
              │
              ▼
         ┌──────────────────┐
         │ Filter by Score  │ ──────► [Keep if score < 1.5]
         └────┬─────────────┘
              │
              ▼
         ┌───────────────────┐
         │ Output Guardrails │ ──────► [Sanitize text]
         └────┬──────────────┘
              │
              ▼
         ┌──────────────────┐
         │  Call GPT-4o     │ ──────► [AI Summary]
         └────┬─────────────┘
              │
              ▼
         ┌──────────────────┐
         │ Redact Response  │ ──────► [Final PII-safe text]
         └────┬─────────────┘
              │
              ▼
         ┌──────────────────┐
         │  Show to User    │
         └──────────────────┘
```

---

## Security Layers

```
Layer 1: Document Upload
├─► Extract text from PDF
├─► Detect PII (8 types)
└─► Redact PII → [TYPE_REDACTED]

Layer 2: Embeddings
├─► Only redacted text is embedded
└─► PII never enters vector store

Layer 3: Input Guardrails
├─► Check query length
├─► Detect prompt injection
├─► Filter inappropriate content
└─► Validate topic relevance

Layer 4: Search Results
├─► Retrieve similar chunks
├─► Filter by relevance threshold
└─► Sanitize output

Layer 5: LLM Prompt
├─► System prompt: "Don't include PII"
├─► User query + sanitized context
└─► No raw documents sent

Layer 6: Response Redaction
├─► Final PII check on LLM output
├─► Catches hallucinated PII
└─► Display only safe text
```

---

## Component Dependencies

```
app.py (Main Application)
├── src/config.py (Settings)
├── src/pii.py (PII Detection & Redaction)
│   └── regex patterns for 8 types
├── src/guardrails.py (Security)
│   ├── InputGuardrails
│   └── OutputGuardrails
├── langchain_text_splitters (Chunking)
├── langchain_community.vectorstores.FAISS (Vector Store)
├── langchain_openai.OpenAIEmbeddings (Embeddings)
└── openai.OpenAI (LLM)
```

---

## External Services

```
┌─────────────────────────────────────────┐
│         SecureMortgageAI App            │
└───────────────┬─────────────────────────┘
                │
                ├─► OpenAI API
                │   ├─► text-embedding-ada-002 (Embeddings)
                │   └─► gpt-4o-mini (Chat Completions)
                │
                └─► Local Services
                    ├─► FAISS (In-memory vector store)
                    ├─► PyPDF (PDF parsing)
                    └─► Streamlit (Web UI)
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Deployment                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Nginx      │  ←────  │  Streamlit   │                 │
│  │ (Reverse     │         │     App      │                 │
│  │   Proxy)     │         │  (Port 8501) │                 │
│  └──────────────┘         └──────┬───────┘                 │
│         ↑                         │                         │
│         │                         ↓                         │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   SSL/TLS    │         │  .env file   │                 │
│  │ (Let's       │         │  (API keys)  │                 │
│  │  Encrypt)    │         └──────────────┘                 │
│  └──────────────┘                                           │
│                                                              │
│  Environment Variables:                                     │
│  • OPENAI_API_KEY=sk-...                                   │
│  • APP_ENV=production                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Metrics

| Operation | Expected Time | Optimization |
|-----------|---------------|--------------|
| PDF Upload (1 page) | 1-2 sec | PyPDF extraction |
| PII Detection | <100ms | Compiled regex |
| Embedding (per chunk) | 200-500ms | OpenAI API |
| Vector Search | <50ms | FAISS index |
| LLM Generation | 2-4 sec | GPT-4o-mini |
| **Total Query Time** | **3-6 sec** | Async operations |

---

## Storage & Memory

```
Per Document:
├─► Raw text: ~2-5 KB (avg)
├─► Chunks (10): ~5 KB
├─► Embeddings (10 × 1536 dims): ~60 KB
└─► Total per doc: ~70 KB

For 100 documents:
├─► Memory: ~7 MB (vectors only)
├─► Temp storage: 0 (in-memory)
└─► Cost: $0.0001/1K tokens (embedding)
```

---

## Technology Stack

```
Frontend:
└─► Streamlit 1.41.1 (Python web framework)

Backend:
├─► Python 3.11.9
├─► LangChain 0.3.14 (Orchestration)
├─► OpenAI API (Embeddings + LLM)
└─► FAISS-CPU 1.13.2 (Vector store)

Security:
├─► Custom PII regex (src/pii.py)
├─► Guardrails (src/guardrails.py)
└─► Multi-layer validation

Document Processing:
├─► PyPDF 5.1.0 (PDF parsing)
└─► RecursiveCharacterTextSplitter (Chunking)

Environment:
├─► python-dotenv (Config)
├─► .env file (Secrets)
└─► requirements.txt (Dependencies)
```

---

**This architecture ensures:**
✅ PII is never exposed  
✅ Malicious queries are blocked  
✅ Responses are accurate and cited  
✅ Performance is optimized  
✅ System is scalable

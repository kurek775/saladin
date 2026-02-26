# Saladin Backend

> **Work in Progress**

FastAPI backend for the Saladin multi-agent orchestration platform. Manages agent lifecycle, task execution via LangGraph, and real-time event broadcasting over WebSockets.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # then edit .env with your API key(s)
uvicorn app.main:app --reload --port 8001
```

## Architecture

```
app/
├── main.py              # FastAPI app, CORS, lifespan (broadcast loop)
├── config.py            # Pydantic settings from .env
│
├── agents/
│   ├── graph.py         # LangGraph state machine (dispatch → review → approve/reject/revise)
│   ├── state.py         # SaladinState, WorkerResult, ReviewResult TypedDicts
│   ├── worker.py        # ReAct worker agent factory (create_react_agent + tools)
│   ├── supervisor.py    # Supervisor review logic, decision parsing
│   ├── prompts.py       # System prompt templates for workers and supervisor
│   ├── tools.py         # search_memory, store_memory LangChain tools
│   ├── llm_factory.py   # Multi-provider LLM factory (Anthropic, OpenAI, Gemini, Ollama)
│   └── callbacks.py     # SaladinCallbackHandler -- bridges LangChain events to event bus
│
├── api/
│   ├── routes/
│   │   ├── agents.py    # GET/POST/PATCH/DELETE /api/agents
│   │   ├── tasks.py     # GET/POST /api/tasks
│   │   └── health.py    # GET /api/health
│   └── websocket.py     # WS /ws with heartbeat
│
├── services/
│   ├── agent_service.py   # Agent CRUD, per-agent status locking
│   ├── task_service.py    # Task creation, background graph execution
│   ├── memory_service.py  # Memory search/store with ChromaDB fallback
│   └── _chroma.py         # ChromaDB client, per-agent collections
│
├── core/
│   ├── store.py         # InMemoryStore (agents dict, tasks dict)
│   ├── event_bus.py     # Async queue-based event bus (max 1000)
│   └── ws_manager.py    # WebSocket connection manager with broadcast
│
└── models/
    ├── domain.py        # AgentConfig, TaskRecord, WorkerOutput, SupervisorReview, enums
    └── schemas.py       # Pydantic request/response schemas
```

## LangGraph Workflow

The orchestration graph is a compiled LangGraph `StateGraph` with these nodes:

1. **dispatch_workers** -- runs all assigned worker agents in parallel via `asyncio.gather()`
2. **review** -- supervisor evaluates combined worker outputs
3. **approve** -- combines outputs into final result, sets task status to APPROVED
4. **reject** -- sets task status to REJECTED with supervisor feedback
5. **revise** -- increments revision counter, clears outputs, loops back to dispatch_workers

Routing after review is handled by `should_continue()`:
- `approve` if decision is "approve"
- `revise` if decision is "revise" and `current_revision < max_revisions`
- `approve` (auto) if revise requested but max revisions reached
- `reject` if decision is "reject"

Worker outputs are truncated before supervisor review: 4 KB per worker, 12 KB total.

## Workers

Each worker is a LangGraph `create_react_agent` with:
- Custom system prompt (from agent config + revision feedback)
- Tools: `search_memory(query, agent_id)`, `store_memory(content, agent_id)`
- LLM created via factory with `max_tokens=4096`
- `SaladinCallbackHandler` for real-time event streaming

## LLM Providers

The `create_llm()` factory supports:

| Provider | SDK | Default Model |
|----------|-----|---------------|
| `anthropic` | `langchain-anthropic` | `claude-sonnet-4-20250514` |
| `openai` | `langchain-openai` | `gpt-4o` |
| `gemini` | `langchain-google-genai` | `gemini-2.0-flash` |
| `ollama` | `langchain-ollama` | `llama3` |

Per-agent overrides are supported. Empty provider/model falls back to global settings.

## Event System

Services publish `WSEvent` objects to the `EventBus` async queue. The lifespan broadcast loop consumes events and sends them to all connected WebSocket clients via `ConnectionManager.broadcast()`.

Event types: `agent_update`, `task_update`, `log`, `worker_output`, `supervisor_review`, `ping`.

## Data Models

**AgentConfig**: id, name, role (worker/supervisor), system_prompt, llm_provider, llm_model, status (idle/busy/error), created_at

**TaskRecord**: id, description, status (pending/running/under_review/revision/approved/rejected/failed), assigned_agents, worker_outputs, supervisor_reviews, current_revision, max_revisions, final_output, created_at, updated_at

## Tests

```bash
pytest
```

- `test_api.py` -- API endpoint tests (agent and task CRUD)
- `test_graph.py` -- Graph routing logic tests (`should_continue` function)

## Key Dependencies

- `fastapi` + `uvicorn` -- ASGI web framework
- `langgraph` + `langchain-core` -- agent orchestration
- `langchain-anthropic`, `langchain-openai`, `langchain-google-genai`, `langchain-ollama` -- LLM providers
- `chromadb` + `langchain-chroma` + `sentence-transformers` -- vector memory
- `pydantic-settings` -- configuration
- `websockets` -- real-time communication

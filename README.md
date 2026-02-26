# Saladin

> **Work in Progress** -- This project is under active development. Features, APIs, and architecture may change.

Saladin is a multi-agent orchestration platform that coordinates AI worker agents to complete tasks through a supervisor-driven review and revision loop. It provides a real-time web dashboard for creating agents, submitting tasks, and monitoring execution as it happens.

## How It Works

You define **worker agents** (each with their own system prompt and optional LLM override), submit a **task**, and a **supervisor agent** reviews the workers' outputs -- approving, rejecting, or requesting revisions.

```
User submits task
       |
       v
 Dispatch Workers (run in parallel)
       |
       v
 Workers produce outputs (ReAct agents with tool access)
       |
       v
 Supervisor reviews all outputs
       |
       +---> Approve --> Done (final output saved)
       |
       +---> Reject  --> Task failed
       |
       +---> Revise  --> Workers re-execute with supervisor feedback
                         (up to MAX_REVISIONS, default 3, then auto-approve)
```

The entire flow is orchestrated as a **LangGraph state machine**. All state changes stream to the frontend in real time over WebSockets.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, LangGraph, LangChain |
| Frontend | React 19, TypeScript, Vite, TailwindCSS |
| State (client) | Zustand |
| Data fetching | TanStack React Query |
| Dashboard layout | react-grid-layout |
| LLM Providers | Anthropic, OpenAI, Google Gemini, Ollama |
| Agent Memory | ChromaDB (vector embeddings via sentence-transformers) |
| Real-time | WebSockets |
| Animations | Framer Motion |

## Project Structure

```
saladin/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph graph, workers, supervisor, prompts, LLM factory, callbacks
│   │   ├── api/routes/      # REST endpoints (agents, tasks, health)
│   │   ├── api/websocket.py # WebSocket endpoint
│   │   ├── services/        # Agent, task, memory, and ChromaDB services
│   │   ├── core/            # In-memory store, event bus, WS connection manager
│   │   ├── models/          # Domain entities and Pydantic schemas
│   │   ├── config.py        # Settings (loaded from .env)
│   │   └── main.py          # FastAPI app entry point
│   ├── tests/               # pytest (test_api.py, test_graph.py)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/           # LandingPage, DashboardPage, TasksPage, TaskDetailPage, AgentsPage
│   │   ├── components/
│   │   │   ├── layout/      # MainLayout, Sidebar, Header
│   │   │   ├── dashboard/   # StatsWidget, ActiveTasksWidget, ActiveAgentsWidget, DashboardWidget
│   │   │   ├── tasks/       # TaskSubmitForm, TaskTable, TaskTimeline
│   │   │   ├── agents/      # AgentList, AgentCard, AgentStatusBadge
│   │   │   ├── logs/        # LiveLogPanel, LogEntry
│   │   │   └── common/      # ErrorBoundary, LoadingSpinner, StatusBadge, SplashScreen, Logo
│   │   ├── store/           # Zustand slices (agents, tasks, logs, theme, dashboard layouts)
│   │   ├── api/             # HTTP client and TypeScript types
│   │   ├── hooks/           # useAgents, useTasks, useWebSocket, useMousePosition
│   │   └── App.tsx          # Router
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
└── .env.example             # Environment variable template
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- At least one LLM provider API key (Anthropic, OpenAI, Google, or a running Ollama instance)

### Setup

1. **Configure environment**

   ```bash
   cp .env.example backend/.env
   ```

   Edit `backend/.env` and add your API key(s).

2. **Backend**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8001
   ```

3. **Frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The frontend runs on `http://localhost:5173` and proxies `/api` and `/ws` requests to the backend on port 8001.

## Configuration

All configuration is done through environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Default LLM provider (`anthropic`, `openai`, `gemini`, `ollama`) | `anthropic` |
| `LLM_MODEL` | Default model name | `claude-sonnet-4-20250514` |
| `ANTHROPIC_API_KEY` | Anthropic API key | -- |
| `OPENAI_API_KEY` | OpenAI API key | -- |
| `GOOGLE_API_KEY` | Google Gemini API key | -- |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_data` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:5173"]` |
| `MAX_REVISIONS` | Max supervisor revision loops | `3` |
| `WS_HEARTBEAT_INTERVAL` | WebSocket heartbeat interval (seconds) | `30` |

Individual agents can override the global LLM provider and model.

## Features

### Agent Management
- Create worker and supervisor agents with custom system prompts
- Pick LLM provider and model per agent (Anthropic, OpenAI, Gemini, Ollama) or inherit global defaults
- Real-time agent status tracking (idle / busy / error)
- Full CRUD -- create, update, delete agents

### Task Execution
- Submit tasks with a description and assign to specific agents (or auto-assign all workers)
- Workers execute concurrently via `asyncio.gather()` using LangGraph's ReAct agent pattern
- Each worker has access to `search_memory` and `store_memory` tools
- Supervisor reviews combined outputs (truncated to 4 KB per worker, 12 KB total) and decides: **approve**, **reject**, or **revise**
- On revise, workers re-execute with the supervisor's feedback injected into their prompt
- Auto-approves at max revisions if the supervisor keeps requesting revisions
- Task statuses: `pending` → `running` → `under_review` → `approved` / `rejected` / `revision` / `failed`

### Agent Memory
- Workers have access to `search_memory` and `store_memory` tools
- Backed by ChromaDB with per-agent vector collections (using sentence-transformers embeddings)
- Falls back gracefully to in-memory substring matching if ChromaDB is unavailable

### Real-time Dashboard
- Draggable/resizable widget grid (react-grid-layout) with layout persistence
- Stats overview, active tasks, active agents widgets
- Live terminal-style log panel with search filtering and auto-scroll
- Task detail page with timeline of worker outputs and supervisor reviews per revision
- Dark / light / system theme with localStorage persistence

### Landing Page
- Animated hero with matrix rain effect and SVG agent network visualization
- Feature highlights and architecture diagram
- Parallax mouse-tracking effects

## Frontend Routes

| Path | Page | Description |
|------|------|-------------|
| `/` | Landing | Hero page with feature overview |
| `/dashboard` | Dashboard | Real-time stats, logs, and activity widgets |
| `/tasks` | Tasks | Submit new tasks + task history table |
| `/tasks/:id` | Task Detail | Timeline view of a single task's execution |
| `/agents` | Agents | Create and manage agents |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/agents` | List all agents |
| `POST` | `/api/agents` | Create an agent |
| `GET` | `/api/agents/{id}` | Get agent by ID |
| `PATCH` | `/api/agents/{id}` | Update an agent |
| `DELETE` | `/api/agents/{id}` | Delete an agent |
| `GET` | `/api/tasks` | List all tasks (summary) |
| `POST` | `/api/tasks` | Create and run a task |
| `GET` | `/api/tasks/{id}` | Get full task detail |
| `WS` | `/ws` | WebSocket for real-time events |

### WebSocket Events

| Event Type | Description |
|------------|-------------|
| `agent_update` | Agent created, updated, deleted, or status changed |
| `task_update` | Task status changed |
| `log` | System log (LLM start/end, tool invocations, errors) |
| `worker_output` | A worker finished producing output |
| `supervisor_review` | Supervisor made a decision |
| `ping` | Heartbeat keepalive |

## Running Tests

```bash
cd backend
pytest
```

Tests cover API endpoint behavior (`test_api.py`) and graph routing logic (`test_graph.py`).

## Architecture Notes

- **In-memory store** -- agents and tasks live in a Python dict (`InMemoryStore`). No database yet.
- **Event bus** -- async queue (max 1000 events) that bridges service-layer events to WebSocket broadcasts. Drops oldest events on overflow.
- **Per-agent locks** -- `asyncio.Lock` per agent prevents race conditions on status updates during concurrent task execution.
- **Background task tracking** -- running tasks are held in a `set[asyncio.Task]` to prevent garbage collection.
- **LLM factory** -- lazy-imports provider SDKs so only the installed provider needs to be present.
- **Graph caching** -- the compiled LangGraph state machine is built once and reused across all task runs.

## Current Limitations

- **In-memory storage** -- all data is lost on backend restart (no database persistence yet)
- **No authentication** -- the API is open, intended for local development only
- **Single-instance** -- no horizontal scaling or distributed task execution
- **No task update/delete** -- tasks are immutable once created
- **Supervisor is a single global agent** -- not yet configurable per task

## License

TBD

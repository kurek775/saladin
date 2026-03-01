# Saladin

Saladin is an advanced AI agent orchestration platform designed to empower developers to build, deploy, and manage complex multi-agent workflows with ease. It provides a robust backend for agent execution, a real-time frontend for interaction, and flexible deployment options.

## 🚀 Features & Highlights

*   **Multi-Agent Workflows**: Orchestrate sophisticated AI agent interactions and task execution.
*   **Recursive Self-Improvement**: One-click "Self-Improve" launches a scout that analyzes the codebase, creates improvement tasks, and each task can auto-spawn follow-ups up to a configurable depth — a fully autonomous improvement flywheel.
*   **BYOK Multi-Provider LLM**: Bring your own API keys for various LLM providers (OpenAI, Anthropic, Google, Ollama) for flexible model usage.
*   **Human-in-the-Loop Approval**: Integrate human oversight and approval steps into agent workflows.
*   **Task Lineage & Safety Limits**: Auto-created tasks track parent/child relationships with configurable depth limits, per-task child caps, and a global kill switch.
*   **Docker Sandbox & Local Execution**: Securely execute agent code in isolated Docker containers or directly on the host for development.
*   **Real-time WebSocket Communication**: Interact with agents and receive live updates through a responsive WebSocket interface.
*   **Comprehensive Telemetry**: Gain insights into agent behavior and system performance with detailed logging and metrics.
*   **Flexible Storage Backends**: Choose between in-memory, SQLite, or PostgreSQL for persistent data storage.
*   **Background Task Processing**: Utilize Redis and `arq` for efficient asynchronous task handling.

## 🛠️ Tech Stack

**Backend (Python)**:
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs.
*   **LangGraph**: For defining and executing stateful, multi-actor applications with LLMs.
*   **Pydantic Settings**: For robust environment variable management.
*   **ChromaDB**: A vector database for managing agent memories and knowledge.
*   **Redis**: In-memory data store, used for caching and as a message broker for `arq` background tasks.
*   **PostgreSQL**: (Optional) Relational database for persistent storage.
*   **Docker**: For sandboxed code execution and containerized deployment.

**Frontend (React/TypeScript)**:
*   **React**: A declarative, component-based JavaScript library for building user interfaces.
*   **TypeScript**: A strongly typed superset of JavaScript that compiles to plain JavaScript.
*   **Vite**: A fast development server and build tool for modern web projects.
*   **Zustand**: A small, fast, and scalable bear-bones state-management solution.
*   **Tailwind CSS**: A utility-first CSS framework for rapidly building custom designs.
*   **Framer Motion**: A production-ready motion library for React.
*   **React Router DOM**: For declarative routing in React applications.

## ⚡ Quick Start

### Prerequisites

*   Docker and Docker Compose (recommended for easy setup)
*   Python 3.10+ (if running backend locally)
*   Node.js and npm/yarn (if running frontend locally)

### 1. Using Docker Compose (Recommended)

This will set up the backend API, a PostgreSQL database, a Redis instance, and an ARQ worker.

1.  **Create a `.env` file** in the `backend/` directory based on `backend/.env.example` (if available, otherwise refer to key environment variables below).
    ```bash
    cp backend/.env.example backend/.env # If .env.example exists
    # Or manually create backend/.env with POSTGRES_PASSWORD
    ```
2.  **Start the services**:
    ```bash
    docker compose up --build -d
    ```
3.  The backend API will be available at `http://localhost:8001`.

### 2. Running Backend Locally

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```
2.  **Create a virtual environment and install dependencies**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file** in the `backend/` directory. At minimum, define `POSTGRES_PASSWORD` if using the Docker Compose PostgreSQL, or set `STORAGE_BACKEND=memory` for a simpler start.
4.  **Run the FastAPI application**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    ```
    The backend API will be available at `http://localhost:8001`.

### 3. Running Frontend Locally

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    # or yarn install
    ```
3.  **Start the development server**:
    ```bash
    npm run dev
    # or yarn dev
    ```
    The frontend will typically be available at `http://localhost:5173`.

## ⚙️ Key Environment Variables

These variables can be set in `backend/.env` or as environment variables in your deployment.

*   `LLM_PROVIDER`: Default LLM provider (e.g., `anthropic`, `openai`, `google`).
*   `LLM_MODEL`: Default LLM model to use.
*   `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`: API keys for respective LLM providers. (Optional if using BYOK headers).
*   `OLLAMA_BASE_URL`: URL for an Ollama instance, if used.
*   `STORAGE_BACKEND`: `memory` (default), `sqlite`, or `postgres`.
*   `DATABASE_URL`: Connection string for the database (e.g., `sqlite:///./saladin.db` or `postgresql://user:pass@host:port/db`).
*   `CHROMA_PERSIST_DIR`: Directory for ChromaDB persistence (e.g., `./chroma_data`).
*   `CORS_ORIGINS`: Comma-separated list of allowed CORS origins for the frontend (e.g., `http://localhost:5173`).
*   `REDIS_URL`: URL for the Redis instance (e.g., `redis://localhost:6379`).
*   `USE_QUEUE`: Set to `true` to enable the ARQ queue for background tasks.
*   `SANDBOX_MODE`: `local` (default) or `docker`. Controls how code is executed.
*   `WORKSPACE_DIR`: Directory where agent workspaces are stored (e.g., `./workspace`).
*   `SANDBOX_IMAGE`: Docker image to use for the sandbox (e.g., `python:3.13-slim`).
*   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: PostgreSQL credentials (used with Docker Compose).

### Self-Improvement Settings

*   `MAX_TASK_DEPTH`: Maximum depth for auto-spawned task trees (default: `3`).
*   `MAX_CHILD_TASKS_PER_TASK`: Max children any single task can spawn (default: `5`).
*   `MAX_TOTAL_AUTO_TASKS`: Global cap on total auto-created tasks (default: `20`).
*   `ALLOW_AUTO_TASK_CREATION`: Kill switch to disable auto-task creation entirely (default: `true`).

## 🧠 Self-Improvement Loop

Saladin agents can analyze and improve their own codebase. Click **Self-Improve** in the sidebar to configure and launch:

```
User clicks "Self-Improve" → configures (tasks: 5, depth: 2) → hits Launch
  └─ Scout task analyzes codebase, creates 5 improvement tasks
       ├─ Task 1 does work, notices more issues → spawns 2 follow-ups
       │   ├─ Task 1.1 does work (depth 2, can't spawn more)
       │   └─ Task 1.2 does work (depth 2, can't spawn more)
       ├─ Task 2 does work → spawns 1 follow-up
       │   └─ Task 2.1 does work (depth 2, stops)
       └─ Tasks 3-5 do work, log observations to IMPROVEMENTS.md
```

**Agent tools:**
- `create_task` — spawn follow-up tasks (respects depth/count limits)
- `append_improvement_note` — log observations to `IMPROVEMENTS.md` for future reference

**Safety:** All auto-spawning is bounded by depth limits, per-task child caps, a global task ceiling, and a kill switch (`ALLOW_AUTO_TASK_CREATION=false`).

# Saladin Frontend

> **Work in Progress**

React 19 + TypeScript frontend for the Saladin multi-agent orchestration platform. Provides a real-time dashboard for creating agents, submitting tasks, and monitoring execution via WebSockets.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. The Vite dev server proxies `/api` and `/ws` to the backend at `http://localhost:8001`.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Type-check + production build |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview production build |

## Architecture

```
src/
├── App.tsx                # React Router setup
├── main.tsx               # Entry point
│
├── pages/
│   ├── LandingPage.tsx    # Hero with matrix rain, agent network SVG, feature cards
│   ├── DashboardPage.tsx  # Draggable widget grid (react-grid-layout) with stats, logs, activity
│   ├── TasksPage.tsx      # Task submit form + task history table
│   ├── TaskDetailPage.tsx # Task timeline (worker outputs + supervisor reviews per revision)
│   └── AgentsPage.tsx     # Agent creation form + deployed agent list
│
├── components/
│   ├── layout/            # MainLayout, Sidebar, Header
│   ├── dashboard/         # StatsWidget, ActiveTasksWidget, ActiveAgentsWidget, DashboardWidget
│   ├── tasks/             # TaskSubmitForm, TaskTable, TaskTimeline
│   ├── agents/            # AgentList, AgentCard, AgentStatusBadge
│   ├── logs/              # LiveLogPanel (terminal-style with search + auto-scroll), LogEntry
│   └── common/            # ErrorBoundary, LoadingSpinner, StatusBadge, SplashScreen, Logo
│
├── store/                 # Zustand state management
│   ├── index.ts           # Combined AppStore
│   ├── agentSlice.ts      # agents: Record<id, Agent>, upsert/remove/status updates
│   ├── taskSlice.ts       # tasks: Record<id, TaskSummary>, upsert/status updates
│   ├── logSlice.ts        # logs: LogEntry[] (keeps last 200)
│   ├── themeSlice.ts      # theme: light/dark/system (persisted to localStorage)
│   └── dashboardSlice.ts  # dashboard layouts (react-grid-layout, persisted to localStorage)
│
├── api/
│   ├── client.ts          # Fetch wrapper for all REST endpoints
│   └── types.ts           # TypeScript interfaces (Agent, Task, LogEntry, WSEvent, etc.)
│
├── hooks/
│   ├── useAgents.ts       # useAgents, useCreateAgent, useUpdateAgent, useDeleteAgent
│   ├── useTasks.ts        # useTasks, useTask, useCreateTask
│   ├── useWebSocket.ts    # Auto-connecting WS with exponential backoff reconnect
│   └── useMousePosition.ts # Normalized mouse tracking for parallax effects
│
└── styles/
    └── index.css          # Tailwind imports + custom styles
```

## Routes

| Path | Page | Layout |
|------|------|--------|
| `/` | LandingPage | Standalone (no sidebar) |
| `/dashboard` | DashboardPage | MainLayout |
| `/tasks` | TasksPage | MainLayout |
| `/tasks/:id` | TaskDetailPage | MainLayout |
| `/agents` | AgentsPage | MainLayout |

## State Management

Zustand store with five slices:

- **agentSlice** -- agents map, synced from REST queries and WebSocket `agent_update` events
- **taskSlice** -- tasks map, synced from REST queries and WebSocket `task_update` events
- **logSlice** -- rolling log buffer (200 entries max), fed by `log`, `worker_output`, and `supervisor_review` WebSocket events
- **themeSlice** -- light/dark/system theme, persisted to `localStorage` key `saladin-theme`
- **dashboardSlice** -- react-grid-layout positions, persisted to `localStorage` key `saladin-dashboard-layouts`

## Real-time Updates

`useWebSocket` hook connects to `/ws` and handles:

| WS Event | Action |
|----------|--------|
| `agent_update` | Upsert or remove agent in store |
| `task_update` | Update task status in store |
| `log` | Append to log buffer |
| `worker_output` | Append to log buffer |
| `supervisor_review` | Append to log buffer |
| `ping` | Ignored (keepalive) |

Reconnects with exponential backoff (up to 30s delay) on disconnect.

## API Client

All calls go through `src/api/client.ts`:

| Function | Method | Endpoint |
|----------|--------|----------|
| `fetchAgents()` | GET | `/api/agents` |
| `fetchAgent(id)` | GET | `/api/agents/{id}` |
| `createAgent(data)` | POST | `/api/agents` |
| `updateAgent(id, data)` | PATCH | `/api/agents/{id}` |
| `deleteAgent(id)` | DELETE | `/api/agents/{id}` |
| `fetchTasks()` | GET | `/api/tasks` |
| `fetchTask(id)` | GET | `/api/tasks/{id}` |
| `createTask(data)` | POST | `/api/tasks` |

## Key Dependencies

- `react` 19 + `react-dom` + `react-router-dom` 7 -- UI framework and routing
- `@tanstack/react-query` -- server state and caching
- `zustand` -- client state management
- `react-grid-layout` -- draggable/resizable dashboard widgets
- `framer-motion` -- animations and transitions
- `tailwindcss` -- utility-first CSS (dark mode via class strategy)
- `lucide-react` -- icons
- `clsx` + `tailwind-merge` -- conditional class merging

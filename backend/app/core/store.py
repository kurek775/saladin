from app.models.domain import AgentConfig, TaskRecord


class InMemoryStore:
    def __init__(self) -> None:
        self.agents: dict[str, AgentConfig] = {}
        self.tasks: dict[str, TaskRecord] = {}


store = InMemoryStore()

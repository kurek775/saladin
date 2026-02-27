import asyncio
import dataclasses

from app.models.domain import AgentConfig, AgentRole, AgentStatus
from app.models.schemas import AgentCreate, AgentUpdate, WSEvent
from app.core.event_bus import event_bus
from app.core.repository import get_agent_repo

# Per-agent locks for status updates
_agent_locks: dict[str, asyncio.Lock] = {}


def list_agents(skip: int = 0, limit: int = 100) -> list[AgentConfig]:
    return get_agent_repo().list(skip, limit)


def agent_count() -> int:
    return get_agent_repo().count()


def get_agent(agent_id: str) -> AgentConfig | None:
    return get_agent_repo().get(agent_id)


def get_workers() -> list[AgentConfig]:
    return [a for a in get_agent_repo().list(0, 10000) if a.role == AgentRole.WORKER]


async def create_agent(data: AgentCreate) -> AgentConfig:
    agent = AgentConfig(
        name=data.name,
        role=data.role,
        system_prompt=data.system_prompt,
        llm_provider=data.llm_provider,
        llm_model=data.llm_model,
    )
    get_agent_repo().save(agent)
    await event_bus.publish(WSEvent(
        type="agent_update",
        data={"action": "created", "agent": _agent_dict(agent)},
    ))
    return agent


async def update_agent(agent_id: str, data: AgentUpdate) -> AgentConfig | None:
    repo = get_agent_repo()
    agent = repo.get(agent_id)
    if agent is None:
        return None
    updates = {}
    if data.name is not None:
        updates["name"] = data.name
    if data.system_prompt is not None:
        updates["system_prompt"] = data.system_prompt
    if data.llm_provider is not None:
        updates["llm_provider"] = data.llm_provider
    if data.llm_model is not None:
        updates["llm_model"] = data.llm_model
    if updates:
        agent = dataclasses.replace(agent, **updates)
        repo.save(agent)
    await event_bus.publish(WSEvent(
        type="agent_update",
        data={"action": "updated", "agent": _agent_dict(agent)},
    ))
    return agent


async def delete_agent(agent_id: str) -> bool:
    deleted = get_agent_repo().delete(agent_id)
    if not deleted:
        return False
    _agent_locks.pop(agent_id, None)
    await event_bus.publish(WSEvent(
        type="agent_update",
        data={"action": "deleted", "agent_id": agent_id},
    ))
    return True


async def set_agent_status(agent_id: str, status: AgentStatus) -> None:
    if agent_id not in _agent_locks:
        _agent_locks[agent_id] = asyncio.Lock()
    async with _agent_locks[agent_id]:
        repo = get_agent_repo()
        agent = repo.get(agent_id)
        if agent:
            updated = dataclasses.replace(agent, status=status)
            repo.save(updated)
            await event_bus.publish(WSEvent(
                type="agent_update",
                data={"action": "status_changed", "agent": _agent_dict(updated)},
            ))


def _agent_dict(agent: AgentConfig) -> dict:
    return {
        "id": agent.id,
        "name": agent.name,
        "role": agent.role.value,
        "system_prompt": agent.system_prompt,
        "llm_provider": agent.llm_provider,
        "llm_model": agent.llm_model,
        "status": agent.status.value,
        "created_at": agent.created_at,
    }

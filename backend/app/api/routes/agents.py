from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.services import agent_service

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def list_agents(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    agents = agent_service.list_agents(skip=skip, limit=limit)
    return [_to_response(a) for a in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    agent = agent_service.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _to_response(agent)


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(data: AgentCreate):
    agent = await agent_service.create_agent(data)
    return _to_response(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, data: AgentUpdate):
    agent = await agent_service.update_agent(agent_id, data)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _to_response(agent)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    deleted = await agent_service.delete_agent(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")


def _to_response(agent) -> dict:
    return {
        "id": agent.id,
        "name": agent.name,
        "role": agent.role.value if hasattr(agent.role, 'value') else agent.role,
        "system_prompt": agent.system_prompt,
        "llm_provider": agent.llm_provider,
        "llm_model": agent.llm_model,
        "status": agent.status.value if hasattr(agent.status, 'value') else agent.status,
        "created_at": agent.created_at,
    }

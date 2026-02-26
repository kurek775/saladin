import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_create_agent(client: AsyncClient):
    resp = await client.post("/api/agents", json={
        "name": "TestWorker",
        "role": "worker",
        "system_prompt": "You are a test worker.",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "TestWorker"
    assert data["role"] == "worker"
    assert "id" in data


@pytest.mark.anyio
async def test_list_agents(client: AsyncClient):
    resp = await client.get("/api/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_create_and_get_agent(client: AsyncClient):
    create_resp = await client.post("/api/agents", json={
        "name": "Agent2",
        "role": "worker",
    })
    agent_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/agents/{agent_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == agent_id


@pytest.mark.anyio
async def test_delete_agent(client: AsyncClient):
    create_resp = await client.post("/api/agents", json={"name": "ToDelete"})
    agent_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/agents/{agent_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/agents/{agent_id}")
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_create_task(client: AsyncClient):
    # Create a worker first
    await client.post("/api/agents", json={"name": "Worker1"})

    resp = await client.post("/api/tasks", json={
        "description": "Write a hello world program",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "Write a hello world program"
    assert "id" in data


@pytest.mark.anyio
async def test_list_tasks(client: AsyncClient):
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

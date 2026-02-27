import pytest
import httpx
from httpx import ASGITransport
from app.main import app

@pytest.fixture(scope="function")
async def async_client():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health_endpoint(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_health_details_endpoint(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/health/details")
    assert response.status_code == 200
    json_response = response.json()
    expected_fields = [
        "status",
        "uptime",
        "num_agents",
        "num_tasks",
        "python_version",
        "sandbox_mode",
        "llm_provider",
        "llm_model",
    ]
    for field in expected_fields:
        assert field in json_response
    assert json_response["status"] == "ok"

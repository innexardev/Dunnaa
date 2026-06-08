import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_ready_check(client: AsyncClient):
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] is True


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    await client.get("/health")
    response = await client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "requests_total" in data
    assert data["requests_total"] >= 1


@pytest.mark.asyncio
async def test_request_id_header(client: AsyncClient):
    response = await client.get("/health")
    assert response.headers.get("x-request-id")

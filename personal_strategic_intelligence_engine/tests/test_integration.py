"""Integration tests for PSIE platform."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app


@pytest.fixture
async def app():
    """Create test app."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_config_readiness_endpoint(client):
    """Test config readiness endpoint returns structured data."""
    response = await client.get("/health/config-readiness")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "overall" in data
    assert "core" in data
    assert "database" in data
    assert "llm" in data
    assert "execution" in data
    assert "safety" in data
    
    # Check overall status is valid
    valid_statuses = ["READY", "PARTIAL", "MISSING", "UNSAFE"]
    assert data["overall"]["status"] in valid_statuses


@pytest.mark.asyncio
async def test_profile_list_endpoint(client):
    """Test profile list endpoint."""
    response = await client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert "profiles" in data


@pytest.mark.asyncio
async def test_kernel_status_endpoint(client):
    """Test kernel status endpoint."""
    response = await client.get("/kernel/status")
    assert response.status_code == 200
    data = response.json()
    
    # Check kernel status fields
    assert "mode" in data
    assert "cycle_number" in data
    assert "execution_enabled" in data


@pytest.mark.asyncio
async def test_kernel_priorities_endpoint(client):
    """Test kernel priorities endpoint."""
    response = await client.get("/kernel/priorities")
    assert response.status_code == 200
    data = response.json()
    assert "priorities" in data


@pytest.mark.asyncio
async def test_kernel_policies_endpoint(client):
    """Test kernel policies endpoint."""
    response = await client.get("/kernel/policies")
    assert response.status_code == 200
    data = response.json()
    assert "policies" in data


@pytest.mark.asyncio
async def test_signals_endpoint(client):
    """Test signals endpoint."""
    response = await client.get("/signals")
    assert response.status_code == 200
    data = response.json()
    assert "signals" in data


@pytest.mark.asyncio
async def test_governance_goals_endpoint(client):
    """Test governance goals endpoint."""
    response = await client.get("/governance/goals")
    assert response.status_code == 200
    data = response.json()
    assert "goals" in data


@pytest.mark.asyncio
async def test_intelligence_dashboard_endpoint(client):
    """Test intelligence dashboard endpoint."""
    response = await client.get("/intelligence/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "dashboard" in data or "forecasts" in data or "trends" in data


@pytest.mark.asyncio
async def test_execution_pending_endpoint(client):
    """Test execution pending endpoint."""
    response = await client.get("/execution/pending")
    assert response.status_code == 200
    data = response.json()
    assert "executions" in data


@pytest.mark.asyncio
async def test_debate_sessions_endpoint(client):
    """Test debate sessions endpoint."""
    response = await client.get("/debate/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data


@pytest.mark.asyncio
async def test_learning_memories_endpoint(client):
    """Test learning memories endpoint."""
    response = await client.get("/learning/memories")
    assert response.status_code == 200
    data = response.json()
    assert "memories" in data


@pytest.mark.asyncio
async def test_simulation_runs_endpoint(client):
    """Test simulation runs endpoint."""
    response = await client.get("/simulation/runs")
    assert response.status_code == 200
    data = response.json()
    assert "runs" in data or "simulations" in data

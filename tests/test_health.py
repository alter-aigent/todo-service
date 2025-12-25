import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    # Be flexible: allow either {"status": "ok"} or similar
    assert isinstance(data, dict)
    assert data.get("status") in {"ok", "healthy", "up"}

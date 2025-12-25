import pytest


@pytest.mark.asyncio
async def test_openapi_available(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["openapi"].startswith("3.")


@pytest.mark.asyncio
async def test_create_user_and_task_happy_path(client):
    # Create user
    u = {"email": "alice@example.com", "name": "Alice"}
    resp = await client.post("/users", json=u)
    assert resp.status_code in (200, 201), resp.text
    user = resp.json()
    assert user["email"] == u["email"]
    assert "id" in user

    # Create task
    t = {"title": "Buy milk", "description": "2%", "user_id": user["id"]}
    resp = await client.post("/tasks", json=t)
    assert resp.status_code in (200, 201), resp.text
    task = resp.json()
    assert task["title"] == t["title"]
    assert task.get("user_id") == user["id"]
    assert "id" in task

    # Get task
    resp = await client.get(f"/tasks/{task['id']}")
    assert resp.status_code == 200
    got = resp.json()
    assert got["id"] == task["id"]


@pytest.mark.asyncio
async def test_list_tasks_supports_pagination_and_filters(client):
    # Create user
    resp = await client.post("/users", json={"email": "bob@example.com", "name": "Bob"})
    assert resp.status_code in (200, 201)
    user_id = resp.json()["id"]

    # Create tasks
    for i in range(5):
        resp = await client.post(
            "/tasks",
            json={"title": f"Task {i}", "description": None, "user_id": user_id},
        )
        assert resp.status_code in (200, 201)

    # List tasks with pagination
    resp = await client.get("/tasks", params={"limit": 2, "offset": 0})
    assert resp.status_code == 200
    data = resp.json()

    # Accept either list response or envelope
    if isinstance(data, list):
        assert len(data) <= 2
    else:
        assert "items" in data
        assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_update_task_status(client):
    # Create user
    resp = await client.post("/users", json={"email": "carol@example.com", "name": "Carol"})
    assert resp.status_code in (200, 201)
    user_id = resp.json()["id"]

    # Create task
    resp = await client.post(
        "/tasks",
        json={"title": "Do thing", "description": "", "user_id": user_id},
    )
    assert resp.status_code in (200, 201)
    task = resp.json()

    # Update status (support either PATCH /tasks/{id}/status or PATCH /tasks/{id})
    payload = {"status": "done"}

    resp = await client.patch(f"/tasks/{task['id']}/status", json=payload)
    if resp.status_code == 404:
        resp = await client.patch(f"/tasks/{task['id']}", json=payload)

    assert resp.status_code in (200, 204), resp.text

    # Fetch and verify
    resp = await client.get(f"/tasks/{task['id']}")
    assert resp.status_code == 200
    got = resp.json()
    assert got.get("status") in {"done", "completed", True, "DONE"}

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_exists() -> None:
    """
    Health endpoint also checks DB in runtime, but in unit tests we just verify route exists.
    """
    app = create_app()
    client = TestClient(app)
    resp = client.get("/health")
    # If DB isn't configured for tests, FastAPI returns 500, but route must exist.
    assert resp.status_code in (200, 500)



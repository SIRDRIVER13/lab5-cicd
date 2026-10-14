"""Testy jednostkowe - uruchamiane na bazie SQLite w pamięci, bez Dockera."""
import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'test.db'}")
    app.config["TESTING"] = True
    return app.test_client()


def test_index_returns_version(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["app"] == "Task API"
    assert "version" in resp.get_json()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["database"] == "ok"


def test_create_and_list_tasks(client):
    resp = client.post("/tasks", json={"title": "Napisać Dockerfile"})
    assert resp.status_code == 201
    assert resp.get_json()["done"] is False
    tasks = client.get("/tasks").get_json()
    assert [t["title"] for t in tasks] == ["Napisać Dockerfile"]


def test_create_task_requires_title(client):
    resp = client.post("/tasks", json={"title": "  "})
    assert resp.status_code == 400


def test_mark_task_done(client):
    task_id = client.post("/tasks", json={"title": "Skonfigurować CI/CD"}).get_json()["id"]
    resp = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert resp.status_code == 200
    assert resp.get_json()["done"] is True


def test_mark_missing_task_returns_404(client):
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404

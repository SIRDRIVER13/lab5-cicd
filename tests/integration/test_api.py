"""Testy integracyjne - uruchamiane na działającej aplikacji (docker compose / Kubernetes).

Adres aplikacji podaje się w zmiennej BASE_URL, np. BASE_URL=http://localhost:8000
"""
import os
import time

import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def wait_for_app(timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.get(f"{BASE_URL}/health", timeout=3).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    raise RuntimeError(f"Aplikacja pod {BASE_URL} nie odpowiada")


def setup_module():
    wait_for_app()


def test_health_checks_database():
    body = requests.get(f"{BASE_URL}/health", timeout=5).json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_full_task_flow_against_real_database():
    created = requests.post(f"{BASE_URL}/tasks", json={"title": "Test integracyjny"}, timeout=5)
    assert created.status_code == 201
    task_id = created.json()["id"]

    done = requests.patch(f"{BASE_URL}/tasks/{task_id}", json={"done": True}, timeout=5)
    assert done.status_code == 200
    assert done.json()["done"] is True

    titles = [t["title"] for t in requests.get(f"{BASE_URL}/tasks", timeout=5).json()]
    assert "Test integracyjny" in titles

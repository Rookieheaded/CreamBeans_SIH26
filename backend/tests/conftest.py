import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_IN_MEMORY_DB", "true")

import pytest
from fastapi.testclient import TestClient

from backend.database.in_memory import InMemoryRepository
from backend.main import app
from backend.api.auth import get_current_auth_user


@pytest.fixture(autouse=True)
def reset_db():
    InMemoryRepository.reset()
    app.dependency_overrides[get_current_auth_user] = lambda: {"id": "test-auth-user", "email": "dev@example.com", "phone": None}
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def found_item(client):
    payload = {
        "category": "bag",
        "description": "Dark Lenovo laptop bag with a small tear on the side pocket",
        "image_url": "https://example.com/img1.jpg",
        "location": "Library Lawn",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "timestamp": "2026-08-29T11:00:00Z",
        "reporter": {"name": "Rahul", "email": "rahul@example.com", "phone": "+911234567890"},
    }
    return client.post("/items/found", json=payload).json()


@pytest.fixture
def lost_item(client):
    payload = {
        "category": "bag",
        "description": "Lost my dark Lenovo bag near the library",
        "location": "Library Lawn",
        "latitude": 12.9717,
        "longitude": 77.5945,
        "timestamp": "2026-08-29T11:30:00Z",
        "reporter": {"name": "Asha", "email": "asha@example.com", "phone": "+919876543210"},
    }
    return client.post("/items/lost", json=payload).json()

from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.api.auth import get_current_auth_user
from backend.api.auth_routes import login, LoginRequest
from backend.database.supabase_client import get_client
from backend.main import app


def test_protected_items_require_bearer_token():
    app.dependency_overrides.clear()
    try:
        client = TestClient(app)
        r = client.get("/items")
        assert r.status_code == 401
    finally:
        app.dependency_overrides[get_current_auth_user] = (
            lambda: {"id": "test-auth-user", "email": "dev@example.com", "phone": None}
        )


def test_auth_user_dependency_validates_supabase_token(monkeypatch):
    fake_user = SimpleNamespace(id="auth-123", email="test@example.com", phone=None)
    fake_client = SimpleNamespace(
        auth=SimpleNamespace(get_user=lambda token: SimpleNamespace(user=fake_user))
    )
    monkeypatch.setattr("backend.api.auth.get_client", lambda: fake_client)

    from backend.api.auth import get_current_auth_user
    from fastapi.security import HTTPAuthorizationCredentials

    user = get_current_auth_user(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials="jwt-token")
    )
    assert user["id"] == "auth-123"
    assert user["email"] == "test@example.com"


def test_login_delegates_to_supabase_auth(monkeypatch):
    fake_session = SimpleNamespace(
        access_token="access-token",
        expires_in=3600,
    )
    fake_response = SimpleNamespace(
        session=fake_session,
        user=SimpleNamespace(id="auth-123", email="test@example.com"),
    )
    fake_client = SimpleNamespace(
        auth=SimpleNamespace(
            sign_in_with_password=lambda payload: fake_response
        )
    )
    monkeypatch.setattr("backend.api.auth_routes.get_client", lambda: fake_client)

    result = login(LoginRequest(email="test@example.com", password="secret"))
    assert result.access_token == "access-token"
    assert result.user_id == "auth-123"
    assert result.token_type == "bearer"

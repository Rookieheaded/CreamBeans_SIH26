"""Supabase Auth integration for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.database.supabase_client import get_client

bearer = HTTPBearer(auto_error=False)


def get_current_auth_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Supabase access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization scheme must be Bearer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()

    # Never accept a token with an extra Bearer prefix.
    if token.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed Authorization header. Use: Bearer <access_token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Supabase verifies the JWT and returns the authenticated user.
        response = get_client().auth.get_user(token)

        user = getattr(response, "user", None)

        if user is None:
            raise ValueError("Supabase returned no authenticated user")

        if not getattr(user, "id", None):
            raise ValueError("Supabase user has no user ID")

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Supabase access token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return {
        "id": user.id,
        "email": user.email,
        "phone": getattr(user, "phone", None),
    }

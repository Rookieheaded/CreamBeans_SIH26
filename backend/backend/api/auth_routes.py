"""Supabase Auth login endpoint.

The backend does not implement its own authentication system. Credentials are
sent to Supabase Auth, which returns the session/access token.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from backend.database.supabase_client import get_client

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    user_id: str
    email: EmailStr | None = None


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    try:
        session = get_client().auth.sign_in_with_password(
            {"email": str(payload.email), "password": payload.password}
        )
        if not session.session or not session.user:
            raise ValueError("Supabase Auth returned no session")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Supabase authentication failed: {exc}",
        ) from exc

    return LoginResponse(
        access_token=session.session.access_token,
        expires_in=getattr(session.session, "expires_in", None),
        user_id=session.user.id,
        email=session.user.email,
    )

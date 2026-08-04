from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.auth import ADMIN_PASSWORD

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    if payload.password.strip() != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"ok": True}


# TEMPORARY diagnostic route — remove after debugging.
# Does NOT reveal the password, only its length and first/last character,
# so we can check if Render's env var is set correctly without exposing it.
@router.get("/debug-password-check")
def debug_password_check():
    return {
        "server_password_length": len(ADMIN_PASSWORD),
        "server_password_first_char": ADMIN_PASSWORD[0] if ADMIN_PASSWORD else None,
        "server_password_last_char": ADMIN_PASSWORD[-1] if ADMIN_PASSWORD else None,
    }
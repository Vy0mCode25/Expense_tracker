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
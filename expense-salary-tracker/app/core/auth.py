import os
from fastapi import Header, HTTPException

# Set this via environment variable in production (Render dashboard -> Environment).
# Falls back to a default for local dev only.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


def verify_admin(x_admin_password: str = Header(None)):
    """Every protected route requires this header: X-Admin-Password: <password>"""
    if not x_admin_password or x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid or missing password")
    return True

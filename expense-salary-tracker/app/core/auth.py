import os
from fastapi import Header, HTTPException

# Set this via environment variable in production (Render dashboard -> Environment).
# Falls back to a default for local dev only.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123").strip()


def verify_admin(x_admin_password: str = Header(None)):
    """Every protected route requires this header: X-Admin-Password: <password>"""
    provided = (x_admin_password or "").strip()
    if not provided or provided != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid or missing password")
    return True
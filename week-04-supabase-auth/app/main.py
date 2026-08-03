"""A secure API using Supabase Auth. Week 4 assignment A4."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .supabase_client import supabase

app = FastAPI(
    title="Auth API",
    description="Secure API with Supabase Auth — signup, login, logout, protected routes. Week 4 assignment A4.",
    version="4.0.0",
)


class Credentials(BaseModel):
    email: str | None = None
    password: str | None = None


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok", "supabase": "connected"}


# --- Open auth routes (Stage 1) -----------------------------------------------
@app.post("/auth/signup", status_code=201, summary="Create a new user account")
def signup(body: Credentials):
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_up(
            {"email": body.email, "password": body.password}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user": result.user}


@app.post("/auth/login", summary="Authenticate and return a JWT")
def login(body: Credentials):
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    if result.session is None:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "token_type": "bearer",
    }

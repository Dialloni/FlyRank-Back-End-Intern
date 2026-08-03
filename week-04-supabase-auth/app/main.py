"""A secure API using Supabase Auth. Five doors:
  POST /auth/signup        (open)   create account
  POST /auth/login         (open)   return a JWT
  POST /auth/logout        (guard)  end the session
  GET  /protected/profile  (guard)  private profile
  GET  /public/info        (open)   public data
We never store a password or hash anything — Supabase does that."""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from .auth import get_current_user
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


@app.post("/auth/logout", status_code=204, summary="End the user's session")
def logout(user=Depends(get_current_user)):
    supabase.auth.sign_out()
    return


# --- Public route (Stage 2) ---------------------------------------------------
@app.get("/public/info", summary="Read public, open data")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


# --- Protected routes (Stage 3 verify, Stage 4 reusable guard) ----------------
@app.get("/protected/profile", summary="Read private profile data")
def profile(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@app.get("/protected/dashboard", summary="A second protected route (same guard)")
def dashboard(user=Depends(get_current_user)):
    # No new auth code — reuses the one guard. That reuse is the whole point.
    return {"message": f"Welcome back, {user.email}. This is your dashboard."}

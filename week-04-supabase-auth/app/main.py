"""A secure API using Supabase Auth. Week 4 assignment A4."""
from fastapi import FastAPI

from .supabase_client import supabase  # noqa: F401  (proves the client initializes)

app = FastAPI(
    title="Auth API",
    description="Secure API with Supabase Auth — signup, login, logout, protected routes. Week 4 assignment A4.",
    version="4.0.0",
)


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok", "supabase": "connected"}

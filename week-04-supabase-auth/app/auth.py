"""The guard (Stage 3/4). One reusable dependency that verifies the bearer token
with Supabase and hands the route the current user. HTTPBearer makes the padlock
appear in Swagger UI automatically."""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .supabase_client import supabase

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """Verify the token with Supabase. Missing/malformed header -> 401.
    Invalid/expired token -> 401. Valid -> returns the Supabase user."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Access token required")

    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)  # network call to Supabase = trustworthy
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if response is None or response.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.user

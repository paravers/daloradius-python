"""
Authentication API Routes

Placeholder for authentication endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_auth():
    return {"message": "Auth API working"}
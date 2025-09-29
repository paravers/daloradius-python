"""
Users API Routes

Placeholder for user management endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_users():
    return {"message": "Users API working"}
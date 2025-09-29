"""
System API Routes

Placeholder for system endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_system():
    return {"message": "System API working"}
"""
Reports API Routes

Placeholder for reports endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_reports():
    return {"message": "Reports API working"}
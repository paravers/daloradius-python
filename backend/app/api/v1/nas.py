"""
NAS API Routes

Placeholder for NAS endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_nas():
    return {"message": "NAS API working"}
"""
Accounting API Routes

Placeholder for accounting endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_accounting():
    return {"message": "Accounting API working"}
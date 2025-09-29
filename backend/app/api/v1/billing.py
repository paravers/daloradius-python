"""
Billing API Routes

Placeholder for billing endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_billing():
    return {"message": "Billing API working"}
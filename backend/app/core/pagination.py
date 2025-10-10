"""
Pagination Support

This module provides pagination utilities for API responses.
"""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field
from fastapi import Query

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for API requests"""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def skip(self) -> int:
        """Calculate skip offset for database queries"""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        arbitrary_types_allowed = True


def create_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """FastAPI dependency for pagination parameters"""
    return PaginationParams(page=page, size=size)

"""
Batch Operations Schemas

This module contains Pydantic schemas for batch operations management,
including batch history tracking and batch operation requests/responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class BatchHistoryBase(BaseModel):
    """Base schema for batch history"""
    batch_name: str = Field(..., min_length=1, max_length=255,
                            description="Name of the batch operation")
    batch_description: Optional[str] = Field(
        None, max_length=1000, description="Description of the batch operation")
    hotspot_id: Optional[int] = Field(
        None, description="Associated hotspot ID")
    operation_type: str = Field(..., min_length=1,
                                max_length=50, description="Type of batch operation")
    operation_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional operation details")
    total_count: int = Field(
        0, ge=0, description="Total number of items in the batch")
    success_count: int = Field(
        0, ge=0, description="Number of successful operations")
    failure_count: int = Field(
        0, ge=0, description="Number of failed operations")
    status: str = Field("pending", description="Batch operation status")

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'running',
                            'completed', 'failed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(
                f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class BatchHistoryCreate(BatchHistoryBase):
    """Schema for creating batch history records"""
    pass


class BatchHistoryUpdate(BaseModel):
    """Schema for updating batch history records"""
    batch_name: Optional[str] = Field(None, min_length=1, max_length=255)
    batch_description: Optional[str] = Field(None, max_length=1000)
    hotspot_id: Optional[int] = None
    operation_details: Optional[Dict[str, Any]] = None
    total_count: Optional[int] = Field(None, ge=0)
    success_count: Optional[int] = Field(None, ge=0)
    failure_count: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'running',
                                'completed', 'failed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(
                    f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class BatchHistoryResponse(BatchHistoryBase):
    """Schema for batch history responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class BatchOperationRequest(BaseModel):
    """Schema for batch operation requests"""
    operation_type: str = Field(..., min_length=1,
                                max_length=50, description="Type of batch operation")
    target_ids: List[int] = Field(..., min_items=1,
                                  description="List of target IDs for the operation")
    operation_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Operation-specific data")
    batch_name: Optional[str] = Field(
        None, max_length=255, description="Optional name for the batch operation")
    batch_description: Optional[str] = Field(
        None, max_length=1000, description="Optional description")
    hotspot_id: Optional[int] = Field(
        None, description="Associated hotspot ID")


class BatchOperationResult(BaseModel):
    """Schema for batch operation results"""
    batch_history_id: int = Field(...,
                                  description="ID of the created batch history record")
    operation_type: str = Field(..., description="Type of operation performed")
    total_count: int = Field(..., ge=0,
                             description="Total number of items processed")
    success_count: int = Field(..., ge=0,
                               description="Number of successful operations")
    failure_count: int = Field(..., ge=0,
                               description="Number of failed operations")
    status: str = Field(..., description="Overall operation status")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of errors encountered")
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional operation details")


class BatchUserOperationRequest(BatchOperationRequest):
    """Schema for batch user operations"""
    operation_type: str = Field(...,
                                regex=r'^(create|delete|update|activate|deactivate)$')


class BatchNasOperationRequest(BatchOperationRequest):
    """Schema for batch NAS operations"""
    operation_type: str = Field(...,
                                regex=r'^(delete|update|activate|deactivate)$')


class BatchGroupOperationRequest(BatchOperationRequest):
    """Schema for batch group operations"""
    operation_type: str = Field(...,
                                regex=r'^(add_users|remove_users|delete|update)$')


# Query schemas
class BatchHistoryQuery(BaseModel):
    """Schema for batch history queries"""
    operation_type: Optional[str] = None
    status: Optional[str] = None
    hotspot_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = Field("created_at")
    sort_order: Optional[str] = Field("desc", regex=r'^(asc|desc)$')


class BatchHistoryListResponse(BaseModel):
    """Schema for batch history list responses"""
    items: List[BatchHistoryResponse]
    total: int
    page: int
    size: int
    pages: int

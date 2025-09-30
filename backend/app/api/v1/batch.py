"""
Batch Operations API

This module provides API endpoints for batch operations management,
including batch history tracking and batch operation execution.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import BatchHistory, User
from app.schemas.batch import (
    BatchHistoryCreate,
    BatchHistoryListResponse,
    BatchHistoryQuery,
    BatchHistoryResponse,
    BatchHistoryUpdate,
    BatchOperationRequest,
    BatchOperationResult,
    BatchUserOperationRequest,
    BatchNasOperationRequest,
    BatchGroupOperationRequest,
)
from app.services.batch_service import BatchService

router = APIRouter(
    prefix="/batch",
    tags=["batch"],
    responses={404: {"description": "Not found"}},
)


@router.get("/history", response_model=BatchHistoryListResponse, summary="Get batch operation history")
async def get_batch_history(
    operation_type: Optional[str] = Query(
        None, description="Filter by operation type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    hotspot_id: Optional[int] = Query(
        None, description="Filter by hotspot ID"),
    created_after: Optional[datetime] = Query(
        None, description="Filter by creation date (after)"),
    created_before: Optional[datetime] = Query(
        None, description="Filter by creation date (before)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query(
        "desc", regex=r'^(asc|desc)$', description="Sort order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve batch operation history with filtering and pagination.
    """
    try:
        # Build query filters
        filters = []
        if operation_type:
            filters.append(BatchHistory.operation_type == operation_type)
        if status:
            filters.append(BatchHistory.status == status)
        if hotspot_id:
            filters.append(BatchHistory.hotspot_id == hotspot_id)
        if created_after:
            filters.append(BatchHistory.created_at >= created_after)
        if created_before:
            filters.append(BatchHistory.created_at <= created_before)

        # Get total count
        total_query = db.query(func.count(BatchHistory.id))
        if filters:
            total_query = total_query.filter(and_(*filters))
        total = total_query.scalar()

        # Build main query
        query = db.query(BatchHistory)
        if filters:
            query = query.filter(and_(*filters))

        # Apply sorting
        if hasattr(BatchHistory, sort_by):
            sort_column = getattr(BatchHistory, sort_by)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)
        else:
            query = query.order_by(desc(BatchHistory.created_at))

        # Apply pagination
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()

        # Calculate pagination info
        pages = (total + size - 1) // size

        return BatchHistoryListResponse(
            items=[BatchHistoryResponse.from_orm(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve batch history: {str(e)}"
        )


@router.get("/history/{batch_id}", response_model=BatchHistoryResponse, summary="Get batch operation details")
async def get_batch_details(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed information about a specific batch operation.
    """
    batch_history = db.query(BatchHistory).filter(
        BatchHistory.id == batch_id).first()
    if not batch_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch operation not found"
        )

    return BatchHistoryResponse.from_orm(batch_history)


@router.post("/history", response_model=BatchHistoryResponse, summary="Create batch history record")
async def create_batch_history(
    batch_data: BatchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new batch history record.
    """
    try:
        batch_history = BatchHistory(
            batch_name=batch_data.batch_name,
            batch_description=batch_data.batch_description,
            hotspot_id=batch_data.hotspot_id,
            operation_type=batch_data.operation_type,
            operation_details=batch_data.operation_details,
            total_count=batch_data.total_count,
            success_count=batch_data.success_count,
            failure_count=batch_data.failure_count,
            status=batch_data.status,
        )

        db.add(batch_history)
        db.commit()
        db.refresh(batch_history)

        return BatchHistoryResponse.from_orm(batch_history)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch history: {str(e)}"
        )


@router.put("/history/{batch_id}", response_model=BatchHistoryResponse, summary="Update batch history record")
async def update_batch_history(
    batch_id: int,
    batch_data: BatchHistoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing batch history record.
    """
    batch_history = db.query(BatchHistory).filter(
        BatchHistory.id == batch_id).first()
    if not batch_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch operation not found"
        )

    try:
        # Update fields if provided
        update_data = batch_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(batch_history, field, value)

        # Update timestamp
        batch_history.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(batch_history)

        return BatchHistoryResponse.from_orm(batch_history)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update batch history: {str(e)}"
        )


@router.delete("/history/{batch_id}", summary="Delete batch history record")
async def delete_batch_history(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a batch history record.
    """
    batch_history = db.query(BatchHistory).filter(
        BatchHistory.id == batch_id).first()
    if not batch_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch operation not found"
        )

    try:
        db.delete(batch_history)
        db.commit()
        return {"message": "Batch history record deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete batch history: {str(e)}"
        )


@router.post("/users", response_model=BatchOperationResult, summary="Execute batch user operations")
async def batch_user_operation(
    operation_request: BatchUserOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute batch operations on users.
    """
    batch_service = BatchService(db)

    try:
        result = await batch_service.execute_user_batch_operation(
            operation_request, current_user
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute batch user operation: {str(e)}"
        )


@router.post("/nas", response_model=BatchOperationResult, summary="Execute batch NAS operations")
async def batch_nas_operation(
    operation_request: BatchNasOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute batch operations on NAS devices.
    """
    batch_service = BatchService(db)

    try:
        result = await batch_service.execute_nas_batch_operation(
            operation_request, current_user
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute batch NAS operation: {str(e)}"
        )


@router.post("/groups", response_model=BatchOperationResult, summary="Execute batch group operations")
async def batch_group_operation(
    operation_request: BatchGroupOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute batch operations on user groups.
    """
    batch_service = BatchService(db)

    try:
        result = await batch_service.execute_group_batch_operation(
            operation_request, current_user
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute batch group operation: {str(e)}"
        )


@router.get("/operations/types", summary="Get available batch operation types")
async def get_operation_types(
    current_user: User = Depends(get_current_user),
):
    """
    Get list of available batch operation types.
    """
    return {
        "user_operations": ["create", "delete", "update", "activate", "deactivate"],
        "nas_operations": ["delete", "update", "activate", "deactivate"],
        "group_operations": ["add_users", "remove_users", "delete", "update"],
    }


@router.get("/stats", summary="Get batch operations statistics")
async def get_batch_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get statistics about batch operations.
    """
    try:
        # Total operations
        total_operations = db.query(func.count(BatchHistory.id)).scalar()

        # Operations by status
        status_stats = db.query(
            BatchHistory.status,
            func.count(BatchHistory.id)
        ).group_by(BatchHistory.status).all()

        # Operations by type
        type_stats = db.query(
            BatchHistory.operation_type,
            func.count(BatchHistory.id)
        ).group_by(BatchHistory.operation_type).all()

        # Recent operations (last 7 days)
        seven_days_ago = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0)
        seven_days_ago = seven_days_ago.replace(day=seven_days_ago.day - 7)

        recent_operations = db.query(func.count(BatchHistory.id)).filter(
            BatchHistory.created_at >= seven_days_ago
        ).scalar()

        return {
            "total_operations": total_operations,
            "recent_operations": recent_operations,
            "status_distribution": dict(status_stats),
            "operation_type_distribution": dict(type_stats),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get batch statistics: {str(e)}"
        )

"""
Batch Operations Service

This module provides business logic for batch operations management,
including executing batch operations and tracking their history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import BatchHistory, User, UserGroup
from app.models.nas import Nas
from app.schemas.batch import (
    BatchOperationResult,
    BatchUserOperationRequest,
    BatchNasOperationRequest,
    BatchGroupOperationRequest,
)


class BatchService:
    """Service for handling batch operations"""

    def __init__(self, db: Session):
        self.db = db

    async def execute_user_batch_operation(
        self,
        operation_request: BatchUserOperationRequest,
        current_user: User
    ) -> BatchOperationResult:
        """Execute batch operations on users"""

        # Create batch history record
        batch_history = BatchHistory(
            batch_name=operation_request.batch_name or f"User {operation_request.operation_type}",
            batch_description=operation_request.batch_description,
            hotspot_id=operation_request.hotspot_id,
            operation_type=f"user_{operation_request.operation_type}",
            operation_details={
                "target_ids": operation_request.target_ids,
                "operation_data": operation_request.operation_data,
                "executed_by": current_user.username,
            },
            total_count=len(operation_request.target_ids),
            success_count=0,
            failure_count=0,
            status="running",
            started_at=datetime.utcnow(),
        )

        self.db.add(batch_history)
        self.db.commit()
        self.db.refresh(batch_history)

        try:
            success_count = 0
            failure_count = 0
            errors = []

            # Execute the operation based on type
            if operation_request.operation_type == "delete":
                success_count, failure_count, errors = await self._batch_delete_users(
                    operation_request.target_ids
                )
            elif operation_request.operation_type == "activate":
                success_count, failure_count, errors = await self._batch_update_user_status(
                    operation_request.target_ids, "active"
                )
            elif operation_request.operation_type == "deactivate":
                success_count, failure_count, errors = await self._batch_update_user_status(
                    operation_request.target_ids, "inactive"
                )
            elif operation_request.operation_type == "update":
                success_count, failure_count, errors = await self._batch_update_users(
                    operation_request.target_ids, operation_request.operation_data
                )
            else:
                raise ValueError(
                    f"Unsupported operation type: {operation_request.operation_type}")

            # Update batch history
            batch_history.success_count = success_count
            batch_history.failure_count = failure_count
            batch_history.status = "completed" if failure_count == 0 else "failed"
            batch_history.completed_at = datetime.utcnow()

            if errors:
                batch_history.error_message = "; ".join(
                    # Store first 5 errors
                    [str(error) for error in errors[:5]])

            self.db.commit()

            return BatchOperationResult(
                batch_history_id=batch_history.id,
                operation_type=operation_request.operation_type,
                total_count=len(operation_request.target_ids),
                success_count=success_count,
                failure_count=failure_count,
                status=batch_history.status,
                errors=errors,
                details={"batch_name": batch_history.batch_name}
            )

        except Exception as e:
            # Update batch history with error
            batch_history.status = "failed"
            batch_history.error_message = str(e)
            batch_history.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    async def _batch_delete_users(self, user_ids: List[int]) -> tuple[int, int, List[Dict[str, Any]]]:
        """Delete multiple users"""
        success_count = 0
        failure_count = 0
        errors = []

        for user_id in user_ids:
            try:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    self.db.delete(user)
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append(
                        {"user_id": user_id, "error": "User not found"})
            except Exception as e:
                failure_count += 1
                errors.append({"user_id": user_id, "error": str(e)})

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            # If commit fails, all operations failed
            return 0, len(user_ids), [{"error": f"Commit failed: {str(e)}"}]

        return success_count, failure_count, errors

    async def _batch_update_user_status(
        self, user_ids: List[int], status: str
    ) -> tuple[int, int, List[Dict[str, Any]]]:
        """Update status for multiple users"""
        success_count = 0
        failure_count = 0
        errors = []

        for user_id in user_ids:
            try:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    user.status = status
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append(
                        {"user_id": user_id, "error": "User not found"})
            except Exception as e:
                failure_count += 1
                errors.append({"user_id": user_id, "error": str(e)})

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return 0, len(user_ids), [{"error": f"Commit failed: {str(e)}"}]

        return success_count, failure_count, errors

    async def _batch_update_users(
        self, user_ids: List[int], update_data: Dict[str, Any]
    ) -> tuple[int, int, List[Dict[str, Any]]]:
        """Update multiple users with provided data"""
        success_count = 0
        failure_count = 0
        errors = []

        for user_id in user_ids:
            try:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    # Update user fields
                    for field, value in update_data.items():
                        if hasattr(user, field):
                            setattr(user, field, value)
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append(
                        {"user_id": user_id, "error": "User not found"})
            except Exception as e:
                failure_count += 1
                errors.append({"user_id": user_id, "error": str(e)})

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return 0, len(user_ids), [{"error": f"Commit failed: {str(e)}"}]

        return success_count, failure_count, errors

    async def execute_nas_batch_operation(
        self,
        operation_request: BatchNasOperationRequest,
        current_user: User
    ) -> BatchOperationResult:
        """Execute batch operations on NAS devices"""

        # Create batch history record
        batch_history = BatchHistory(
            batch_name=operation_request.batch_name or f"NAS {operation_request.operation_type}",
            batch_description=operation_request.batch_description,
            hotspot_id=operation_request.hotspot_id,
            operation_type=f"nas_{operation_request.operation_type}",
            operation_details={
                "target_ids": operation_request.target_ids,
                "operation_data": operation_request.operation_data,
                "executed_by": current_user.username,
            },
            total_count=len(operation_request.target_ids),
            success_count=0,
            failure_count=0,
            status="running",
            started_at=datetime.utcnow(),
        )

        self.db.add(batch_history)
        self.db.commit()
        self.db.refresh(batch_history)

        try:
            success_count = 0
            failure_count = 0
            errors = []

            # Execute the operation based on type
            if operation_request.operation_type == "delete":
                success_count, failure_count, errors = await self._batch_delete_nas(
                    operation_request.target_ids
                )
            elif operation_request.operation_type == "update":
                success_count, failure_count, errors = await self._batch_update_nas(
                    operation_request.target_ids, operation_request.operation_data
                )
            else:
                raise ValueError(
                    f"Unsupported NAS operation type: {operation_request.operation_type}")

            # Update batch history
            batch_history.success_count = success_count
            batch_history.failure_count = failure_count
            batch_history.status = "completed" if failure_count == 0 else "failed"
            batch_history.completed_at = datetime.utcnow()

            if errors:
                batch_history.error_message = "; ".join(
                    [str(error) for error in errors[:5]])

            self.db.commit()

            return BatchOperationResult(
                batch_history_id=batch_history.id,
                operation_type=operation_request.operation_type,
                total_count=len(operation_request.target_ids),
                success_count=success_count,
                failure_count=failure_count,
                status=batch_history.status,
                errors=errors,
                details={"batch_name": batch_history.batch_name}
            )

        except Exception as e:
            batch_history.status = "failed"
            batch_history.error_message = str(e)
            batch_history.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    async def _batch_delete_nas(self, nas_ids: List[int]) -> tuple[int, int, List[Dict[str, Any]]]:
        """Delete multiple NAS devices"""
        success_count = 0
        failure_count = 0
        errors = []

        for nas_id in nas_ids:
            try:
                nas = self.db.query(Nas).filter(Nas.id == nas_id).first()
                if nas:
                    self.db.delete(nas)
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append({"nas_id": nas_id, "error": "NAS not found"})
            except Exception as e:
                failure_count += 1
                errors.append({"nas_id": nas_id, "error": str(e)})

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return 0, len(nas_ids), [{"error": f"Commit failed: {str(e)}"}]

        return success_count, failure_count, errors

    async def _batch_update_nas(
        self, nas_ids: List[int], update_data: Dict[str, Any]
    ) -> tuple[int, int, List[Dict[str, Any]]]:
        """Update multiple NAS devices"""
        success_count = 0
        failure_count = 0
        errors = []

        for nas_id in nas_ids:
            try:
                nas = self.db.query(Nas).filter(Nas.id == nas_id).first()
                if nas:
                    for field, value in update_data.items():
                        if hasattr(nas, field):
                            setattr(nas, field, value)
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append({"nas_id": nas_id, "error": "NAS not found"})
            except Exception as e:
                failure_count += 1
                errors.append({"nas_id": nas_id, "error": str(e)})

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return 0, len(nas_ids), [{"error": f"Commit failed: {str(e)}"}]

        return success_count, failure_count, errors

    async def execute_group_batch_operation(
        self,
        operation_request: BatchGroupOperationRequest,
        current_user: User
    ) -> BatchOperationResult:
        """Execute batch operations on user groups"""

        # Create batch history record
        batch_history = BatchHistory(
            batch_name=operation_request.batch_name or f"Group {operation_request.operation_type}",
            batch_description=operation_request.batch_description,
            hotspot_id=operation_request.hotspot_id,
            operation_type=f"group_{operation_request.operation_type}",
            operation_details={
                "target_ids": operation_request.target_ids,
                "operation_data": operation_request.operation_data,
                "executed_by": current_user.username,
            },
            total_count=len(operation_request.target_ids),
            success_count=0,
            failure_count=0,
            status="running",
            started_at=datetime.utcnow(),
        )

        self.db.add(batch_history)
        self.db.commit()
        self.db.refresh(batch_history)

        try:
            success_count = 0
            failure_count = 0
            errors = []

            # Execute the operation based on type
            if operation_request.operation_type == "delete":
                success_count, failure_count, errors = await self._batch_delete_groups(
                    operation_request.target_ids
                )
            elif operation_request.operation_type == "update":
                success_count, failure_count, errors = await self._batch_update_groups(
                    operation_request.target_ids, operation_request.operation_data
                )
            else:
                raise ValueError(
                    f"Unsupported group operation type: {operation_request.operation_type}")

            # Update batch history
            batch_history.success_count = success_count
            batch_history.failure_count = failure_count
            batch_history.status = "completed" if failure_count == 0 else "failed"
            batch_history.completed_at = datetime.utcnow()

            if errors:
                batch_history.error_message = "; ".join(
                    [str(error) for error in errors[:5]])

            self.db.commit()

            return BatchOperationResult(
                batch_history_id=batch_history.id,
                operation_type=operation_request.operation_type,
                total_count=len(operation_request.target_ids),
                success_count=success_count,
                failure_count=failure_count,
                status=batch_history.status,
                errors=errors,
                details={"batch_name": batch_history.batch_name}
            )

        except Exception as e:
            batch_history.status = "failed"
            batch_history.error_message = str(e)
            batch_history.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    async def _batch_delete_groups(self, group_ids: List[int]) -> tuple[int, int, List[Dict[str, Any]]]:
        """Delete multiple user groups"""
        success_count = 0
        failure_count = 0
        errors = []

        for group_id in group_ids:
            try:
                group = self.db.query(UserGroup).filter(
                    UserGroup.id == group_id).first()
                if group:
                    self.db.delete(group)
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append(
                        {"group_id": group_id, "error": "Group not found"})
            except Exception as e:
                failure_count += 1
                errors.append({"group_id": group_id, "error": str(e)})

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return 0, len(group_ids), [{"error": f"Commit failed: {str(e)}"}]

        return success_count, failure_count, errors

    async def _batch_update_groups(
        self, group_ids: List[int], update_data: Dict[str, Any]
    ) -> tuple[int, int, List[Dict[str, Any]]]:
        """Update multiple user groups"""
        success_count = 0
        failure_count = 0
        errors = []

        for group_id in group_ids:
            try:
                group = self.db.query(UserGroup).filter(
                    UserGroup.id == group_id).first()
                if group:
                    for field, value in update_data.items():
                        if hasattr(group, field):
                            setattr(group, field, value)
                    success_count += 1
                else:
                    failure_count += 1
                    errors.append(
                        {"group_id": group_id, "error": "Group not found"})
            except Exception as e:
                failure_count += 1
                errors.append({"group_id": group_id, "error": str(e)})

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return 0, len(group_ids), [{"error": f"Commit failed: {str(e)}"}]

        return success_count, failure_count, errors

"""
Base Service Classes

This module provides base classes for service layer implementations,
including common patterns and utilities for business logic.
"""

from abc import ABC
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..core.exceptions import (
    ValidationException, ConflictException, 
    NotFoundException, ServiceException
)


class BaseService(ABC):
    """
    Base service class providing common utilities and patterns
    for business logic implementations
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that required fields are present"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValidationException(f"Missing required fields: {', '.join(missing_fields)}")
    
    async def validate_unique_fields(
        self, 
        model_class, 
        data: Dict[str, Any], 
        unique_fields: List[str],
        exclude_id: Optional[int] = None
    ) -> None:
        """Validate that unique fields don't conflict with existing records"""
        for field in unique_fields:
            if field in data and data[field] is not None:
                # Check if value already exists
                query = self.db.query(model_class).filter(
                    getattr(model_class, field) == data[field]
                )
                
                if exclude_id:
                    query = query.filter(model_class.id != exclude_id)
                
                existing = await query.first()
                if existing:
                    raise ConflictException(f"{field.replace('_', ' ').title()} '{data[field]}' already exists")
    
    def handle_database_error(self, error: Exception, operation: str) -> None:
        """Handle database errors with appropriate exceptions"""
        if isinstance(error, IntegrityError):
            raise ConflictException(f"Database integrity error during {operation}")
        else:
            raise ServiceException(f"Database error during {operation}: {str(error)}")
    
    async def log_operation(
        self, 
        operation: str, 
        entity_type: str, 
        entity_id: Optional[int] = None,
        user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log service operations for audit trail"""
        # This would integrate with the logging system
        # For now, just a placeholder
        pass


class CrudService(BaseService):
    """
    Extended base service with common CRUD operation patterns
    """
    
    def __init__(self, db_session: AsyncSession, repository):
        super().__init__(db_session)
        self.repository = repository
    
    async def get_by_id(self, entity_id: int, model_name: str = "Entity"):
        """Get entity by ID with error handling"""
        entity = await self.repository.get(entity_id)
        if not entity:
            raise NotFoundException(f"{model_name} with ID {entity_id} not found")
        return entity
    
    async def create_entity(
        self, 
        create_data, 
        model_name: str = "Entity",
        unique_fields: Optional[List[str]] = None
    ):
        """Create entity with validation"""
        try:
            if unique_fields:
                await self.validate_unique_fields(
                    self.repository.model, 
                    create_data.dict(), 
                    unique_fields
                )
            
            return await self.repository.create(create_data)
            
        except Exception as e:
            self.handle_database_error(e, f"creating {model_name}")
    
    async def update_entity(
        self, 
        entity_id: int, 
        update_data, 
        model_name: str = "Entity",
        unique_fields: Optional[List[str]] = None
    ):
        """Update entity with validation"""
        try:
            # Check if entity exists
            entity = await self.get_by_id(entity_id, model_name)
            
            if unique_fields:
                await self.validate_unique_fields(
                    self.repository.model, 
                    update_data.dict(exclude_unset=True), 
                    unique_fields,
                    exclude_id=entity_id
                )
            
            return await self.repository.update(entity_id, update_data)
            
        except Exception as e:
            self.handle_database_error(e, f"updating {model_name}")
    
    async def delete_entity(
        self, 
        entity_id: int, 
        model_name: str = "Entity",
        soft_delete: bool = False
    ):
        """Delete entity with validation"""
        try:
            # Check if entity exists
            await self.get_by_id(entity_id, model_name)
            
            if soft_delete:
                # Implement soft delete logic
                return await self.repository.soft_delete(entity_id)
            else:
                return await self.repository.delete(entity_id)
                
        except Exception as e:
            self.handle_database_error(e, f"deleting {model_name}")


# Export classes
__all__ = ["BaseService", "CrudService"]
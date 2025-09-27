"""
Base Repository Pattern Implementation

This module provides the base repository class that implements common
CRUD operations for all data models using SQLAlchemy async session.
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.exc import IntegrityError, NoResultFound
from abc import ABC, abstractmethod

from ..db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Base repository class providing common CRUD operations
    """
    
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        """
        Initialize repository with model and database session
        
        Args:
            model: SQLAlchemy model class
            db_session: Async database session
        """
        self.model = model
        self.db = db_session

    async def get(self, id: int, load_relationships: bool = False) -> Optional[ModelType]:
        """
        Get a single record by ID
        
        Args:
            id: Record ID
            load_relationships: Whether to load related objects
            
        Returns:
            Model instance or None if not found
        """
        query = select(self.model).where(self.model.id == id)
        
        if load_relationships:
            query = self._add_relationship_loading(query)
            
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(
        self, 
        field_name: str, 
        field_value: Any, 
        load_relationships: bool = False
    ) -> Optional[ModelType]:
        """
        Get a single record by any field
        
        Args:
            field_name: Field name to search by
            field_value: Field value to match
            load_relationships: Whether to load related objects
            
        Returns:
            Model instance or None if not found
        """
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} has no field {field_name}")
            
        query = select(self.model).where(getattr(self.model, field_name) == field_value)
        
        if load_relationships:
            query = self._add_relationship_loading(query)
            
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        load_relationships: bool = False
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field filters
            order_by: Field name to order by
            order_desc: Whether to order descending
            load_relationships: Whether to load related objects
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)
            
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            field = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(field.desc())
            else:
                query = query.order_by(field)
                
        # Apply relationship loading
        if load_relationships:
            query = self._add_relationship_loading(query)
            
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching records
        """
        query = select(func.count(self.model.id))
        
        if filters:
            query = self._apply_filters(query, filters)
            
        result = await self.db.execute(query)
        return result.scalar()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record
        
        Args:
            obj_in: Pydantic schema with creation data
            
        Returns:
            Created model instance
            
        Raises:
            IntegrityError: If unique constraints are violated
        """
        if hasattr(obj_in, 'dict'):
            obj_data = obj_in.dict()
        else:
            obj_data = dict(obj_in)
            
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        
        try:
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.db.rollback()
            raise e

    async def create_multi(self, objects_in: List[CreateSchemaType]) -> List[ModelType]:
        """
        Create multiple records in a single transaction
        
        Args:
            objects_in: List of Pydantic schemas with creation data
            
        Returns:
            List of created model instances
        """
        db_objects = []
        
        for obj_in in objects_in:
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict()
            else:
                obj_data = dict(obj_in)
                
            db_obj = self.model(**obj_data)
            db_objects.append(db_obj)
            self.db.add(db_obj)
            
        try:
            await self.db.commit()
            
            # Refresh all objects
            for db_obj in db_objects:
                await self.db.refresh(db_obj)
                
            return db_objects
        except IntegrityError as e:
            await self.db.rollback()
            raise e

    async def update(
        self, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record
        
        Args:
            db_obj: Existing model instance
            obj_in: Pydantic schema or dict with update data
            
        Returns:
            Updated model instance
        """
        if hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
            
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
                
        try:
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.db.rollback()
            raise e

    async def delete(self, id: int) -> bool:
        """
        Delete a record by ID
        
        Args:
            id: Record ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0

    async def delete_multi(self, ids: List[int]) -> int:
        """
        Delete multiple records by IDs
        
        Args:
            ids: List of record IDs to delete
            
        Returns:
            Number of deleted records
        """
        query = delete(self.model).where(self.model.id.in_(ids))
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount

    async def exists(self, id: int) -> bool:
        """
        Check if a record exists by ID
        
        Args:
            id: Record ID to check
            
        Returns:
            True if exists, False otherwise
        """
        query = select(func.count(self.model.id)).where(self.model.id == id)
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0

    async def exists_by_field(self, field_name: str, field_value: Any) -> bool:
        """
        Check if a record exists by any field
        
        Args:
            field_name: Field name to check
            field_value: Field value to match
            
        Returns:
            True if exists, False otherwise
        """
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} has no field {field_name}")
            
        query = select(func.count(self.model.id)).where(
            getattr(self.model, field_name) == field_value
        )
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Apply filters to query
        
        Args:
            query: SQLAlchemy query
            filters: Dictionary of field filters
            
        Returns:
            Filtered query
        """
        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                
                if isinstance(field_value, dict):
                    # Handle operators like {'>=': 100}
                    for op, value in field_value.items():
                        if op == '>=':
                            query = query.where(field >= value)
                        elif op == '<=':
                            query = query.where(field <= value)
                        elif op == '>':
                            query = query.where(field > value)
                        elif op == '<':
                            query = query.where(field < value)
                        elif op == '!=':
                            query = query.where(field != value)
                        elif op == 'like':
                            query = query.where(field.like(f"%{value}%"))
                        elif op == 'ilike':
                            query = query.where(field.ilike(f"%{value}%"))
                        elif op == 'in':
                            query = query.where(field.in_(value))
                        elif op == 'not_in':
                            query = query.where(~field.in_(value))
                elif isinstance(field_value, list):
                    # Handle list as IN clause
                    query = query.where(field.in_(field_value))
                else:
                    # Direct equality
                    query = query.where(field == field_value)
                    
        return query

    @abstractmethod
    def _add_relationship_loading(self, query):
        """
        Add relationship loading to query - must be implemented by subclasses
        
        Args:
            query: SQLAlchemy query
            
        Returns:
            Query with relationship loading
        """
        return query

    async def bulk_update(
        self, 
        filters: Dict[str, Any], 
        update_data: Dict[str, Any]
    ) -> int:
        """
        Bulk update records matching filters
        
        Args:
            filters: Dictionary of field filters to match records
            update_data: Dictionary of fields to update
            
        Returns:
            Number of updated records
        """
        query = update(self.model)
        
        # Apply filters
        if filters:
            conditions = []
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    conditions.append(field == field_value)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Apply updates
        query = query.values(**update_data)
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount

    async def search(
        self,
        search_term: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Search records across multiple text fields
        
        Args:
            search_term: Text to search for
            search_fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Additional filters to apply
            
        Returns:
            List of matching model instances
        """
        query = select(self.model)
        
        # Build search conditions
        search_conditions = []
        for field_name in search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                search_conditions.append(field.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.where(or_(*search_conditions))
        
        # Apply additional filters
        if filters:
            query = self._apply_filters(query, filters)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
"""
Hotspot Repository

This module provides data access layer functionality for hotspot management.
Handles CRUD operations and complex queries for hotspot entities.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func, desc, asc

from app.models.hotspot import Hotspot
from .base import BaseRepository


class HotspotRepository(BaseRepository[Hotspot]):
    """
    Repository class for hotspot data access operations.

    Provides CRUD operations and specialized queries for hotspot management,
    including search, filtering, and pagination functionality.
    """

    def __init__(self, db_session: Session):
        """Initialize hotspot repository with database session."""
        super().__init__(db_session, Hotspot)

    def create(self, hotspot_data: Dict[str, Any], created_by: str = None) -> Hotspot:
        """
        Create a new hotspot record.

        Args:
            hotspot_data: Dictionary containing hotspot field values
            created_by: Username of the operator creating the hotspot

        Returns:
            Created Hotspot instance

        Raises:
            IntegrityError: If name or MAC address already exists
            ValueError: If validation fails
        """
        # Create hotspot instance from data
        hotspot = Hotspot.from_dict(hotspot_data)

        if created_by:
            hotspot.creationby = created_by
            hotspot.updateby = created_by

        # Validate uniqueness constraints
        errors = hotspot.validate_uniqueness(self.db_session)
        if errors:
            error_msg = "; ".join(errors.values())
            raise ValueError(f"Validation failed: {error_msg}")

        # Save to database
        self.db_session.add(hotspot)
        self.db_session.commit()
        self.db_session.refresh(hotspot)

        return hotspot

    def update(self, hotspot_id: int, hotspot_data: Dict[str, Any], updated_by: str = None) -> Optional[Hotspot]:
        """
        Update an existing hotspot record.

        Args:
            hotspot_id: ID of the hotspot to update
            hotspot_data: Dictionary containing updated field values
            updated_by: Username of the operator updating the hotspot

        Returns:
            Updated Hotspot instance or None if not found

        Raises:
            IntegrityError: If name or MAC address conflicts with another record
            ValueError: If validation fails
        """
        hotspot = self.get_by_id(hotspot_id)
        if not hotspot:
            return None

        # Update fields from data
        hotspot.update_from_dict(hotspot_data, updated_by)

        # Validate uniqueness constraints (excluding current record)
        errors = hotspot.validate_uniqueness(
            self.db_session, exclude_id=hotspot_id)
        if errors:
            error_msg = "; ".join(errors.values())
            raise ValueError(f"Validation failed: {error_msg}")

        # Save changes
        self.db_session.commit()
        self.db_session.refresh(hotspot)

        return hotspot

    def delete(self, hotspot_id: int) -> bool:
        """
        Delete a hotspot record by ID.

        Args:
            hotspot_id: ID of the hotspot to delete

        Returns:
            True if deleted successfully, False if not found
        """
        hotspot = self.get_by_id(hotspot_id)
        if not hotspot:
            return False

        self.db_session.delete(hotspot)
        self.db_session.commit()

        return True

    def get_by_name(self, name: str) -> Optional[Hotspot]:
        """
        Get hotspot by name.

        Args:
            name: Hotspot name to search for

        Returns:
            Hotspot instance or None if not found
        """
        return self.db_session.query(Hotspot).filter(Hotspot.name == name).first()

    def get_by_mac(self, mac: str) -> Optional[Hotspot]:
        """
        Get hotspot by MAC/IP address.

        Args:
            mac: MAC or IP address to search for

        Returns:
            Hotspot instance or None if not found
        """
        return self.db_session.query(Hotspot).filter(Hotspot.mac == mac).first()

    def search(self,
               query: str = None,
               hotspot_type: str = None,
               owner: str = None,
               company: str = None,
               page: int = 1,
               per_page: int = 20,
               order_by: str = 'name',
               order_type: str = 'asc') -> Tuple[List[Hotspot], int]:
        """
        Search hotspots with filters and pagination.

        Args:
            query: General search query (searches name, mac, owner, company)
            hotspot_type: Filter by hotspot type
            owner: Filter by owner name
            company: Filter by company name
            page: Page number (1-based)
            per_page: Number of records per page
            order_by: Field to order by (name, mac, owner, company, type, creationdate)
            order_type: Order direction ('asc' or 'desc')

        Returns:
            Tuple of (hotspot_list, total_count)
        """
        # Build base query
        db_query = self.db_session.query(Hotspot)

        # Apply filters
        if query:
            search_filter = or_(
                Hotspot.name.ilike(f'%{query}%'),
                Hotspot.mac.ilike(f'%{query}%'),
                Hotspot.owner.ilike(f'%{query}%'),
                Hotspot.company.ilike(f'%{query}%'),
                Hotspot.address.ilike(f'%{query}%'),
                Hotspot.manager.ilike(f'%{query}%')
            )
            db_query = db_query.filter(search_filter)

        if hotspot_type:
            db_query = db_query.filter(Hotspot.type.ilike(f'%{hotspot_type}%'))

        if owner:
            db_query = db_query.filter(Hotspot.owner.ilike(f'%{owner}%'))

        if company:
            db_query = db_query.filter(Hotspot.company.ilike(f'%{company}%'))

        # Get total count
        total = db_query.count()

        # Apply ordering
        valid_order_fields = ['name', 'mac', 'owner',
                              'company', 'type', 'creationdate', 'updatedate']
        if order_by not in valid_order_fields:
            order_by = 'name'

        order_field = getattr(Hotspot, order_by)
        if order_type.lower() == 'desc':
            db_query = db_query.order_by(desc(order_field))
        else:
            db_query = db_query.order_by(asc(order_field))

        # Apply pagination
        offset = (page - 1) * per_page
        hotspots = db_query.offset(offset).limit(per_page).all()

        return hotspots, total

    def get_hotspot_types(self) -> List[str]:
        """
        Get all unique hotspot types.

        Returns:
            List of unique hotspot types
        """
        types = self.db_session.query(Hotspot.type).distinct().filter(
            Hotspot.type.isnot(None),
            Hotspot.type != ''
        ).all()

        return [t[0] for t in types if t[0]]

    def get_companies(self) -> List[str]:
        """
        Get all unique company names.

        Returns:
            List of unique company names
        """
        companies = self.db_session.query(Hotspot.company).distinct().filter(
            Hotspot.company.isnot(None),
            Hotspot.company != ''
        ).all()

        return [c[0] for c in companies if c[0]]

    def get_owners(self) -> List[str]:
        """
        Get all unique owner names.

        Returns:
            List of unique owner names
        """
        owners = self.db_session.query(Hotspot.owner).distinct().filter(
            Hotspot.owner.isnot(None),
            Hotspot.owner != ''
        ).all()

        return [o[0] for o in owners if o[0]]

    def validate_name_unique(self, name: str, exclude_id: int = None) -> bool:
        """
        Check if hotspot name is unique.

        Args:
            name: Name to check
            exclude_id: ID to exclude from check (for updates)

        Returns:
            True if name is unique, False otherwise
        """
        query = self.db_session.query(Hotspot).filter(Hotspot.name == name)
        if exclude_id:
            query = query.filter(Hotspot.id != exclude_id)

        return query.first() is None

    def validate_mac_unique(self, mac: str, exclude_id: int = None) -> bool:
        """
        Check if MAC/IP address is unique.

        Args:
            mac: MAC or IP address to check
            exclude_id: ID to exclude from check (for updates)

        Returns:
            True if MAC/IP is unique, False otherwise
        """
        if not mac:
            return True

        query = self.db_session.query(Hotspot).filter(Hotspot.mac == mac)
        if exclude_id:
            query = query.filter(Hotspot.id != exclude_id)

        return query.first() is None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get hotspot management statistics.

        Returns:
            Dictionary containing statistics
        """
        total_hotspots = self.db_session.query(Hotspot).count()

        # Count by type
        types_count = self.db_session.query(
            Hotspot.type,
            func.count(Hotspot.id)
        ).filter(
            Hotspot.type.isnot(None),
            Hotspot.type != ''
        ).group_by(Hotspot.type).all()

        # Recent hotspots (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_hotspots = self.db_session.query(Hotspot).filter(
            Hotspot.creationdate >= thirty_days_ago
        ).count()

        return {
            'total_hotspots': total_hotspots,
            'recent_hotspots': recent_hotspots,
            'types_distribution': {t[0]: t[1] for t in types_count},
            'unique_types': len(types_count),
            'unique_companies': len(self.get_companies()),
            'unique_owners': len(self.get_owners())
        }

    def bulk_delete(self, hotspot_ids: List[int]) -> int:
        """
        Delete multiple hotspots by their IDs.

        Args:
            hotspot_ids: List of hotspot IDs to delete

        Returns:
            Number of deleted records
        """
        if not hotspot_ids:
            return 0

        deleted_count = self.db_session.query(Hotspot).filter(
            Hotspot.id.in_(hotspot_ids)
        ).delete(synchronize_session=False)

        self.db_session.commit()

        return deleted_count

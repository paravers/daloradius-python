"""
Hotspot Service

Business logic layer for hotspot management operations.
Handles validation, business rules, and coordinates between repository and API layers.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.hotspot import Hotspot
from app.repositories.hotspot import HotspotRepository
from app.core.exceptions import ValidationError, NotFoundError, ConflictError


class HotspotService:
    """
    Service class for hotspot management business logic.
    
    Provides high-level operations for hotspot management including validation,
    business rule enforcement, and coordination between different layers.
    """
    
    def __init__(self, db_session: Session):
        """Initialize hotspot service with database session."""
        self.db_session = db_session
        self.repository = HotspotRepository(db_session)
    
    def create_hotspot(self, hotspot_data: Dict[str, Any], created_by: str = None) -> Hotspot:
        """
        Create a new hotspot with validation and business rules.
        
        Args:
            hotspot_data: Dictionary containing hotspot information
            created_by: Username of the operator creating the hotspot
            
        Returns:
            Created Hotspot instance
            
        Raises:
            ValidationError: If validation fails
            ConflictError: If name or MAC address already exists
        """
        # Validate required fields
        self._validate_required_fields(hotspot_data)
        
        # Clean and normalize data
        cleaned_data = self._clean_hotspot_data(hotspot_data)
        
        try:
            return self.repository.create(cleaned_data, created_by)
        except ValueError as e:
            if "already exists" in str(e):
                raise ConflictError(str(e))
            else:
                raise ValidationError(str(e))
    
    def update_hotspot(self, hotspot_id: int, hotspot_data: Dict[str, Any], updated_by: str = None) -> Hotspot:
        """
        Update an existing hotspot with validation.
        
        Args:
            hotspot_id: ID of the hotspot to update
            hotspot_data: Dictionary containing updated information
            updated_by: Username of the operator updating the hotspot
            
        Returns:
            Updated Hotspot instance
            
        Raises:
            NotFoundError: If hotspot not found
            ValidationError: If validation fails
            ConflictError: If name or MAC address conflicts
        """
        # Check if hotspot exists
        existing_hotspot = self.repository.get_by_id(hotspot_id)
        if not existing_hotspot:
            raise NotFoundError(f"Hotspot with ID {hotspot_id} not found")
        
        # Clean and normalize data
        cleaned_data = self._clean_hotspot_data(hotspot_data, is_update=True)
        
        try:
            return self.repository.update(hotspot_id, cleaned_data, updated_by)
        except ValueError as e:
            if "already exists" in str(e):
                raise ConflictError(str(e))
            else:
                raise ValidationError(str(e))
    
    def delete_hotspot(self, hotspot_id: int) -> bool:
        """
        Delete a hotspot by ID.
        
        Args:
            hotspot_id: ID of the hotspot to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If hotspot not found
        """
        if not self.repository.get_by_id(hotspot_id):
            raise NotFoundError(f"Hotspot with ID {hotspot_id} not found")
        
        return self.repository.delete(hotspot_id)
    
    def get_hotspot(self, hotspot_id: int) -> Hotspot:
        """
        Get a hotspot by ID.
        
        Args:
            hotspot_id: ID of the hotspot to retrieve
            
        Returns:
            Hotspot instance
            
        Raises:
            NotFoundError: If hotspot not found
        """
        hotspot = self.repository.get_by_id(hotspot_id)
        if not hotspot:
            raise NotFoundError(f"Hotspot with ID {hotspot_id} not found")
        
        return hotspot
    
    def get_hotspot_by_name(self, name: str) -> Optional[Hotspot]:
        """
        Get a hotspot by name.
        
        Args:
            name: Name of the hotspot to retrieve
            
        Returns:
            Hotspot instance or None if not found
        """
        return self.repository.get_by_name(name)
    
    def search_hotspots(self,
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
            query: General search query
            hotspot_type: Filter by hotspot type
            owner: Filter by owner name
            company: Filter by company name
            page: Page number (1-based)
            per_page: Number of records per page
            order_by: Field to order by
            order_type: Order direction ('asc' or 'desc')
            
        Returns:
            Tuple of (hotspot_list, total_count)
        """
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        return self.repository.search(
            query=query,
            hotspot_type=hotspot_type,
            owner=owner,
            company=company,
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_type=order_type
        )
    
    def get_all_hotspots(self, page: int = 1, per_page: int = 20) -> Tuple[List[Hotspot], int]:
        """
        Get all hotspots with pagination.
        
        Args:
            page: Page number (1-based)
            per_page: Number of records per page
            
        Returns:
            Tuple of (hotspot_list, total_count)
        """
        return self.search_hotspots(page=page, per_page=per_page)
    
    def get_hotspot_types(self) -> List[str]:
        """
        Get all unique hotspot types.
        
        Returns:
            List of unique hotspot types
        """
        return self.repository.get_hotspot_types()
    
    def get_companies(self) -> List[str]:
        """
        Get all unique company names.
        
        Returns:
            List of unique company names
        """
        return self.repository.get_companies()
    
    def get_owners(self) -> List[str]:
        """
        Get all unique owner names.
        
        Returns:
            List of unique owner names
        """
        return self.repository.get_owners()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get hotspot management statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return self.repository.get_statistics()
    
    def validate_name_availability(self, name: str, exclude_id: int = None) -> bool:
        """
        Check if hotspot name is available.
        
        Args:
            name: Name to check
            exclude_id: ID to exclude from check (for updates)
            
        Returns:
            True if name is available, False otherwise
        """
        return self.repository.validate_name_unique(name, exclude_id)
    
    def validate_mac_availability(self, mac: str, exclude_id: int = None) -> bool:
        """
        Check if MAC/IP address is available.
        
        Args:
            mac: MAC or IP address to check
            exclude_id: ID to exclude from check (for updates)
            
        Returns:
            True if MAC/IP is available, False otherwise
        """
        return self.repository.validate_mac_unique(mac, exclude_id)
    
    def bulk_delete_hotspots(self, hotspot_ids: List[int]) -> int:
        """
        Delete multiple hotspots.
        
        Args:
            hotspot_ids: List of hotspot IDs to delete
            
        Returns:
            Number of deleted records
        """
        if not hotspot_ids:
            return 0
        
        return self.repository.bulk_delete(hotspot_ids)
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """
        Validate that required fields are present and valid.
        
        Args:
            data: Hotspot data dictionary
            
        Raises:
            ValidationError: If required fields are missing or invalid
        """
        required_fields = ['name', 'mac']
        errors = []
        
        for field in required_fields:
            if not data.get(field) or str(data.get(field)).strip() == '':
                errors.append(f"{field} is required")
        
        if errors:
            raise ValidationError("Missing required fields: " + ", ".join(errors))
    
    def _clean_hotspot_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """
        Clean and normalize hotspot data.
        
        Args:
            data: Raw hotspot data
            is_update: Whether this is an update operation
            
        Returns:
            Cleaned data dictionary
        """
        cleaned = {}
        
        # String fields that should be trimmed
        string_fields = [
            'name', 'mac', 'geocode', 'type', 'owner', 'email_owner',
            'manager', 'email_manager', 'address', 'phone1', 'phone2',
            'company', 'companywebsite', 'companyemail', 'companycontact',
            'companyphone'
        ]
        
        for field in string_fields:
            value = data.get(field)
            if value is not None:
                # Trim whitespace and convert empty strings to None
                cleaned_value = str(value).strip()
                cleaned[field] = cleaned_value if cleaned_value else None
        
        # Special handling for specific fields
        if 'name' in cleaned and cleaned['name']:
            # Remove any % characters which might cause issues
            cleaned['name'] = cleaned['name'].replace('%', '')
        
        if 'companywebsite' in cleaned and cleaned['companywebsite']:
            # Ensure website has protocol
            website = cleaned['companywebsite']
            if not website.startswith(('http://', 'https://')):
                cleaned['companywebsite'] = 'http://' + website
        
        return cleaned
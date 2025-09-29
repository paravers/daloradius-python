"""
Hotspot Schemas

Pydantic schemas for hotspot management API validation and serialization.
Provides request/response models for hotspot operations.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class HotspotBase(BaseModel):
    """Base hotspot schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Hotspot name identifier")
    mac: str = Field(..., min_length=1, max_length=200, description="MAC address or IP address")
    geocode: Optional[str] = Field(None, max_length=200, description="Geographic coordinates or location code")
    type: Optional[str] = Field(None, max_length=200, description="Hotspot type or category")
    
    # Owner information
    owner: Optional[str] = Field(None, max_length=200, description="Owner name")
    email_owner: Optional[EmailStr] = Field(None, description="Owner email address")
    
    # Manager information
    manager: Optional[str] = Field(None, max_length=200, description="Manager name")
    email_manager: Optional[EmailStr] = Field(None, description="Manager email address")
    
    # Location and contact details
    address: Optional[str] = Field(None, max_length=200, description="Physical address")
    phone1: Optional[str] = Field(None, max_length=200, description="Primary phone number")
    phone2: Optional[str] = Field(None, max_length=200, description="Secondary phone number")
    
    # Company information
    company: Optional[str] = Field(None, max_length=200, description="Company name")
    companywebsite: Optional[str] = Field(None, max_length=200, description="Company website URL")
    companyemail: Optional[EmailStr] = Field(None, description="Company email address")
    companycontact: Optional[str] = Field(None, max_length=200, description="Company contact person")
    companyphone: Optional[str] = Field(None, max_length=200, description="Company phone number")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate hotspot name."""
        if not v or not v.strip():
            raise ValueError("Hotspot name cannot be empty")
        
        # Remove any % characters
        cleaned = v.strip().replace('%', '')
        if not cleaned:
            raise ValueError("Hotspot name cannot be empty after cleaning")
        
        return cleaned
    
    @validator('mac')
    def validate_mac_or_ip(cls, v):
        """Validate MAC address or IP address format."""
        if not v or not v.strip():
            raise ValueError("MAC/IP address cannot be empty")
        
        cleaned = v.strip()
        
        # MAC address patterns (various formats)
        mac_patterns = [
            r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',  # XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
            r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$',     # XXXX.XXXX.XXXX
            r'^([0-9A-Fa-f]{12})$'                           # XXXXXXXXXXXX
        ]
        
        # IP address pattern
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        # Check if it matches any MAC pattern
        for pattern in mac_patterns:
            if re.match(pattern, cleaned):
                return cleaned
        
        # Check if it matches IP pattern
        if re.match(ip_pattern, cleaned):
            return cleaned
        
        raise ValueError("Invalid MAC address or IP address format")
    
    @validator('companywebsite')
    def validate_website(cls, v):
        """Validate website URL format."""
        if not v:
            return v
        
        cleaned = v.strip()
        if not cleaned:
            return None
        
        # Add protocol if missing
        if not cleaned.startswith(('http://', 'https://')):
            cleaned = 'http://' + cleaned
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(cleaned):
            raise ValueError("Invalid website URL format")
        
        return cleaned


class HotspotCreate(HotspotBase):
    """Schema for creating a new hotspot."""
    pass


class HotspotUpdate(BaseModel):
    """Schema for updating an existing hotspot."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    mac: Optional[str] = Field(None, min_length=1, max_length=200)
    geocode: Optional[str] = Field(None, max_length=200)
    type: Optional[str] = Field(None, max_length=200)
    
    # Owner information
    owner: Optional[str] = Field(None, max_length=200)
    email_owner: Optional[EmailStr] = Field(None)
    
    # Manager information
    manager: Optional[str] = Field(None, max_length=200)
    email_manager: Optional[EmailStr] = Field(None)
    
    # Location and contact details
    address: Optional[str] = Field(None, max_length=200)
    phone1: Optional[str] = Field(None, max_length=200)
    phone2: Optional[str] = Field(None, max_length=200)
    
    # Company information
    company: Optional[str] = Field(None, max_length=200)
    companywebsite: Optional[str] = Field(None, max_length=200)
    companyemail: Optional[EmailStr] = Field(None)
    companycontact: Optional[str] = Field(None, max_length=200)
    companyphone: Optional[str] = Field(None, max_length=200)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate hotspot name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Hotspot name cannot be empty")
            
            # Remove any % characters
            cleaned = v.strip().replace('%', '')
            if not cleaned:
                raise ValueError("Hotspot name cannot be empty after cleaning")
            
            return cleaned
        return v
    
    @validator('mac')
    def validate_mac_or_ip(cls, v):
        """Validate MAC address or IP address format."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("MAC/IP address cannot be empty")
            
            cleaned = v.strip()
            
            # MAC address patterns (various formats)
            mac_patterns = [
                r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
                r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$',
                r'^([0-9A-Fa-f]{12})$'
            ]
            
            # IP address pattern
            ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            
            # Check if it matches any MAC pattern
            for pattern in mac_patterns:
                if re.match(pattern, cleaned):
                    return cleaned
            
            # Check if it matches IP pattern
            if re.match(ip_pattern, cleaned):
                return cleaned
            
            raise ValueError("Invalid MAC address or IP address format")
        
        return v
    
    @validator('companywebsite')
    def validate_website(cls, v):
        """Validate website URL format."""
        if v is not None:
            if not v or not v.strip():
                return None
            
            cleaned = v.strip()
            
            # Add protocol if missing
            if not cleaned.startswith(('http://', 'https://')):
                cleaned = 'http://' + cleaned
            
            # Basic URL validation
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(cleaned):
                raise ValueError("Invalid website URL format")
            
            return cleaned
        
        return v


class HotspotResponse(HotspotBase):
    """Schema for hotspot response data."""
    
    id: int = Field(..., description="Unique hotspot identifier")
    creationdate: Optional[datetime] = Field(None, description="Creation timestamp")
    creationby: Optional[str] = Field(None, description="Created by operator")
    updatedate: Optional[datetime] = Field(None, description="Last update timestamp")
    updateby: Optional[str] = Field(None, description="Last updated by operator")
    
    class Config:
        orm_mode = True


class HotspotListResponse(BaseModel):
    """Schema for paginated hotspot list response."""
    
    hotspots: List[HotspotResponse] = Field(..., description="List of hotspots")
    total: int = Field(..., description="Total number of hotspots")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class HotspotSearchRequest(BaseModel):
    """Schema for hotspot search request."""
    
    query: Optional[str] = Field(None, description="General search query")
    type: Optional[str] = Field(None, description="Filter by hotspot type")
    owner: Optional[str] = Field(None, description="Filter by owner name")
    company: Optional[str] = Field(None, description="Filter by company name")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    order_by: str = Field('name', description="Field to order by")
    order_type: str = Field('asc', regex='^(asc|desc)$', description="Order direction")


class HotspotValidationRequest(BaseModel):
    """Schema for hotspot validation requests."""
    
    name: Optional[str] = Field(None, description="Name to validate")
    mac: Optional[str] = Field(None, description="MAC/IP to validate")
    exclude_id: Optional[int] = Field(None, description="ID to exclude from validation")


class HotspotValidationResponse(BaseModel):
    """Schema for hotspot validation response."""
    
    valid: bool = Field(..., description="Whether the value is valid/available")
    message: Optional[str] = Field(None, description="Validation message")


class HotspotBulkDeleteRequest(BaseModel):
    """Schema for bulk delete request."""
    
    hotspot_ids: List[int] = Field(..., min_items=1, description="List of hotspot IDs to delete")


class HotspotBulkDeleteResponse(BaseModel):
    """Schema for bulk delete response."""
    
    deleted_count: int = Field(..., description="Number of deleted hotspots")
    message: str = Field(..., description="Operation result message")


class HotspotStatisticsResponse(BaseModel):
    """Schema for hotspot statistics response."""
    
    total_hotspots: int = Field(..., description="Total number of hotspots")
    recent_hotspots: int = Field(..., description="Hotspots created in last 30 days")
    unique_types: int = Field(..., description="Number of unique hotspot types")
    unique_companies: int = Field(..., description="Number of unique companies")
    unique_owners: int = Field(..., description="Number of unique owners")
    types_distribution: Dict[str, int] = Field(..., description="Distribution of hotspots by type")


class HotspotOptionsResponse(BaseModel):
    """Schema for hotspot options (dropdowns) response."""
    
    types: List[str] = Field(..., description="Available hotspot types")
    companies: List[str] = Field(..., description="Available company names")
    owners: List[str] = Field(..., description="Available owner names")
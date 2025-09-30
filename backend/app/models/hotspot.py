"""
Hotspot Management Models

This module contains SQLAlchemy models for hotspot management functionality.
Based on the 'hotspots' table structure in the database schema.
"""

from sqlalchemy import Column, BigInteger, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from typing import Optional, Dict, Any
from datetime import datetime
import re

from .base import Base


class Hotspot(Base):
    """
    Hotspot model representing WiFi hotspot locations and their management information.

    This model corresponds to the 'hotspots' table in the database and manages
    WiFi hotspot locations including their physical details, contact information,
    and management data.
    """

    __tablename__ = "hotspots"

    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Core hotspot information
    name = Column(String(200), nullable=True, index=True,
                  comment="Hotspot name identifier")
    mac = Column(String(200), nullable=True, index=True,
                 comment="MAC address or IP address")
    geocode = Column(String(200), nullable=True,
                     comment="Geographic coordinates or location code")
    type = Column(String(200), nullable=True,
                  comment="Hotspot type or category")

    # Owner information
    owner = Column(String(200), nullable=True, comment="Owner name")
    email_owner = Column(String(200), nullable=True,
                         comment="Owner email address")

    # Manager information
    manager = Column(String(200), nullable=True, comment="Manager name")
    email_manager = Column(String(200), nullable=True,
                           comment="Manager email address")

    # Location and contact details
    address = Column(String(200), nullable=True, comment="Physical address")
    phone1 = Column(String(200), nullable=True, comment="Primary phone number")
    phone2 = Column(String(200), nullable=True,
                    comment="Secondary phone number")

    # Company information
    company = Column(String(200), nullable=True, comment="Company name")
    companywebsite = Column(String(200), nullable=True,
                            comment="Company website URL")
    companyemail = Column(String(200), nullable=True,
                          comment="Company email address")
    companycontact = Column(String(200), nullable=True,
                            comment="Company contact person")
    companyphone = Column(String(200), nullable=True,
                          comment="Company phone number")

    # Audit fields
    creationdate = Column(DateTime, default=func.now(),
                          comment="Creation timestamp")
    creationby = Column(String(128), nullable=True,
                        comment="Created by operator")
    updatedate = Column(DateTime, default=func.now(),
                        onupdate=func.now(), comment="Last update timestamp")
    updateby = Column(String(128), nullable=True,
                      comment="Last updated by operator")

    def __repr__(self) -> str:
        return f"<Hotspot(id={self.id}, name='{self.name}', mac='{self.mac}')>"

    @validates('email_owner', 'email_manager', 'companyemail')
    def validate_email(self, key: str, email: str) -> Optional[str]:
        """Validate email addresses"""
        if email is None or email == "":
            return email

        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            raise ValueError(f"Invalid email format for {key}: {email}")

        return email

    @validates('mac')
    def validate_mac_or_ip(self, key: str, mac: str) -> Optional[str]:
        """Validate MAC address or IP address format"""
        if mac is None or mac == "":
            return mac

        # MAC address pattern (various formats)
        mac_patterns = [
            # XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
            r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
            r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$',     # XXXX.XXXX.XXXX
            r'^([0-9A-Fa-f]{12})$'                           # XXXXXXXXXXXX
        ]

        # IP address pattern
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

        # Check if it matches any MAC pattern
        for pattern in mac_patterns:
            if re.match(pattern, mac):
                return mac

        # Check if it matches IP pattern
        if re.match(ip_pattern, mac):
            return mac

        raise ValueError(f"Invalid MAC address or IP address format: {mac}")

    @validates('companywebsite')
    def validate_website(self, key: str, website: str) -> Optional[str]:
        """Validate website URL format"""
        if website is None or website == "":
            return website

        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(website):
            # Try to add http:// if not present
            if not website.startswith(('http://', 'https://')):
                website = 'http://' + website
                if not url_pattern.match(website):
                    raise ValueError(f"Invalid website URL format: {website}")

        return website

    def to_dict(self) -> Dict[str, Any]:
        """Convert hotspot to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'mac': self.mac,
            'geocode': self.geocode,
            'type': self.type,
            'owner': self.owner,
            'email_owner': self.email_owner,
            'manager': self.manager,
            'email_manager': self.email_manager,
            'address': self.address,
            'phone1': self.phone1,
            'phone2': self.phone2,
            'company': self.company,
            'companywebsite': self.companywebsite,
            'companyemail': self.companyemail,
            'companycontact': self.companycontact,
            'companyphone': self.companyphone,
            'creationdate': self.creationdate.isoformat() if self.creationdate else None,
            'creationby': self.creationby,
            'updatedate': self.updatedate.isoformat() if self.updatedate else None,
            'updateby': self.updateby
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hotspot':
        """Create hotspot instance from dictionary"""
        # Filter out None values and non-column fields
        valid_fields = {
            'name', 'mac', 'geocode', 'type', 'owner', 'email_owner',
            'manager', 'email_manager', 'address', 'phone1', 'phone2',
            'company', 'companywebsite', 'companyemail', 'companycontact',
            'companyphone', 'creationby', 'updateby'
        }

        filtered_data = {k: v for k, v in data.items(
        ) if k in valid_fields and v is not None}

        return cls(**filtered_data)

    def update_from_dict(self, data: Dict[str, Any], updated_by: str = None) -> None:
        """Update hotspot fields from dictionary"""
        updateable_fields = {
            'name', 'mac', 'geocode', 'type', 'owner', 'email_owner',
            'manager', 'email_manager', 'address', 'phone1', 'phone2',
            'company', 'companywebsite', 'companyemail', 'companycontact',
            'companyphone'
        }

        for key, value in data.items():
            if key in updateable_fields and value is not None:
                setattr(self, key, value)

        if updated_by:
            self.updateby = updated_by

        # Update timestamp will be handled automatically by onupdate

    def is_name_unique(self, db_session, exclude_id: Optional[int] = None) -> bool:
        """Check if hotspot name is unique"""
        query = db_session.query(Hotspot).filter(Hotspot.name == self.name)
        if exclude_id:
            query = query.filter(Hotspot.id != exclude_id)

        return query.first() is None

    def is_mac_unique(self, db_session, exclude_id: Optional[int] = None) -> bool:
        """Check if MAC/IP address is unique"""
        if not self.mac:
            return True

        query = db_session.query(Hotspot).filter(Hotspot.mac == self.mac)
        if exclude_id:
            query = query.filter(Hotspot.id != exclude_id)

        return query.first() is None

    def validate_uniqueness(self, db_session, exclude_id: Optional[int] = None) -> Dict[str, str]:
        """Validate uniqueness constraints and return any errors"""
        errors = {}

        if self.name and not self.is_name_unique(db_session, exclude_id):
            errors['name'] = f"Hotspot name '{self.name}' already exists"

        if self.mac and not self.is_mac_unique(db_session, exclude_id):
            errors['mac'] = f"MAC/IP address '{self.mac}' already exists"

        return errors

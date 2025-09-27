"""GIS (Geographic Information System) related data models.

These Pydantic models provide a typed abstraction over the legacy PHP code
that manages hotspot geolocation (DALOHOTSPOTS table) and interactive map
operations in `gis-viewmap.php` and `gis-editmap.php`, as well as hotspot
management forms (mng-hs-new.php, mng-hs-edit.php).

Design Principles:
- Field names mirror database column names (snake_case) for clarity
- Aliases provided where the PHP/UI layer uses alternative naming
- Geocode stored as original 'lat,lon' string plus parsed numeric form
- Separate lightweight models for map marker rendering vs full hotspot record
- Audit fields (creation/update) modeled with nullable datetime

Source References:
- gis-viewmap.php (SELECT id, name, mac, geocode)
- gis-editmap.php (INSERT/DELETE with creationdate/by, updatedate/by)
- mng-hs-new.php (INSERT full hotspot record with owner/manager/company/contact fields)
- mng-hs-edit.php (UPDATE full record, full column list SELECT)

If future extensions add hotspot grouping, status, or performance metrics,
new models can extend the base `HotspotBase`.
"""
from __future__ import annotations

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class GeoPoint(BaseModel):
    """Structured geographic coordinate.

    Accepts input as either separate latitude/longitude floats or a single
    comma-separated string (eg: "51.505,-0.09"). "geocode_raw" retains the
    original format from the database/UI while lat/lon provide numeric form.
    """
    geocode_raw: str = Field(..., alias="geocode")
    latitude: float
    longitude: float

    @validator("latitude", "longitude", pre=True, always=True)
    def parse_lat_lon(cls, v, values, field):  # type: ignore[override]
        # If explicit numeric provided, just return
        if isinstance(v, (int, float)):
            return float(v)
        # If missing, try to derive from geocode_raw
        raw = values.get("geocode_raw") or values.get("geocode")
        if raw and isinstance(raw, str) and "," in raw:
            parts = raw.split(",")
            if len(parts) == 2:
                try:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                except ValueError:
                    raise ValueError("Invalid geocode numeric values")
                return lat if field.name == "latitude" else lon
        raise ValueError(f"Unable to derive {field.name} from input")

    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True


class HotspotBase(BaseModel):
    """Base identifying fields for a hotspot."""
    id: Optional[int] = None
    name: str
    mac: str
    geocode: Optional[str] = None  # raw 'lat,lon' string or empty


class HotspotContactInfo(BaseModel):
    """Owner/manager and business contact fields."""
    owner: Optional[str] = None
    email_owner: Optional[str] = None
    manager: Optional[str] = None
    email_manager: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    companywebsite: Optional[str] = None
    companyemail: Optional[str] = None
    companycontact: Optional[str] = None
    companyphone: Optional[str] = None


class HotspotAudit(BaseModel):
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None


class HotspotTypeInfo(BaseModel):
    """Type / classification of hotspot (field 'type' in DB/PHP forms)."""
    type: Optional[str] = None  # free-form in current PHP implementation


class Hotspot(HotspotBase, HotspotContactInfo, HotspotTypeInfo, HotspotAudit):
    """Full hotspot record reflecting DALOHOTSPOTS columns.

    Columns (from mng-hs-new.php INSERT & mng-hs-edit.php SELECT/UPDATE):
      id, name, mac, geocode, owner, email_owner, manager, email_manager,
      address, company, phone1, phone2, type, companywebsite, companyemail,
      companycontact, companyphone, creationdate, creationby, updatedate, updateby
    """
    pass


class HotspotCreate(BaseModel):
    """Input model for creating a hotspot (mirrors required validation)."""
    name: str
    macaddress: str = Field(..., alias="mac")
    geocode: Optional[str] = None
    hotspot_type: Optional[str] = Field(None, alias="type")
    ownername: Optional[str] = Field(None, alias="owner")
    emailowner: Optional[str] = Field(None, alias="email_owner")
    managername: Optional[str] = Field(None, alias="manager")
    emailmanager: Optional[str] = Field(None, alias="email_manager")
    address: Optional[str] = None
    company: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    companywebsite: Optional[str] = None
    companyemail: Optional[str] = None
    companycontact: Optional[str] = None
    companyphone: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True


class HotspotUpdate(BaseModel):
    """Input model for updating hotspot mutable fields."""
    macaddress: Optional[str] = Field(None, alias="mac")
    geocode: Optional[str] = None
    hotspot_type: Optional[str] = Field(None, alias="type")
    ownername: Optional[str] = Field(None, alias="owner")
    emailowner: Optional[str] = Field(None, alias="email_owner")
    managername: Optional[str] = Field(None, alias="manager")
    emailmanager: Optional[str] = Field(None, alias="email_manager")
    address: Optional[str] = None
    company: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    companywebsite: Optional[str] = None
    companyemail: Optional[str] = None
    companycontact: Optional[str] = None
    companyphone: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True


class MapMarker(BaseModel):
    """Lightweight marker used for rendering in Leaflet map.

    Derived from SELECT id, name, mac, geocode WHERE geocode present.
    Includes parsed coordinates for convenience.
    """
    id: int
    name: str
    mac: str
    geocode: str
    latitude: float
    longitude: float

    @classmethod
    def from_hotspot(cls, hotspot: Hotspot) -> "MapMarker":
        if not hotspot.geocode:
            raise ValueError("Hotspot missing geocode")
        parts = hotspot.geocode.split(",")
        if len(parts) != 2:
            raise ValueError("Invalid hotspot geocode format")
        return cls(
            id=hotspot.id or 0,
            name=hotspot.name,
            mac=hotspot.mac,
            geocode=hotspot.geocode,
            latitude=float(parts[0].strip()),
            longitude=float(parts[1].strip()),
        )


class MapView(BaseModel):
    """Collection of markers prepared for map rendering."""
    markers: List[MapMarker] = []

    def bounds(self) -> Optional[dict]:
        """Return leaflet-style bounds (southWest & northEast)."""
        if not self.markers:
            return None
        lats = [m.latitude for m in self.markers]
        lons = [m.longitude for m in self.markers]
        return {
            "southWest": {"lat": min(lats), "lon": min(lons)},
            "northEast": {"lat": max(lats), "lon": max(lons)},
        }


__all__ = [
    "GeoPoint",
    "HotspotBase",
    "HotspotContactInfo",
    "HotspotAudit",
    "HotspotTypeInfo",
    "Hotspot",
    "HotspotCreate",
    "HotspotUpdate",
    "MapMarker",
    "MapView",
]

"""
daloRADIUS User Management Module Data Models

This module contains Pydantic models for all data structures used in the User Management functionality.
These models represent the data structures from the PHP files in app/operators/mng-*.php files.

Models follow SOLID principles:
- SRP: Each model has a single responsibility 
- OCP: Models are extensible through inheritance
- DIP: Models depend on abstractions (base classes)
- ISP: Interfaces are segregated by functionality
- LSP: Derived models can replace base models

Database Tables Covered:
- radcheck: User authentication data
- radreply: User authorization attributes
- radusergroup: User group associations
- userinfo: User profile information
- radgroupcheck: Group check attributes
- radgroupreply: Group reply attributes
- nas: Network Access Server definitions
- operators: System operators
- hotspots: Hotspot definitions
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator, EmailStr
from ipaddress import IPv4Address
import re


class BaseUserModel(BaseModel):
    """Base model for all user management-related data structures"""
    
    class Config:
        # Enable ORM mode for database integration
        orm_mode = True
        # Use enum values instead of enum names
        use_enum_values = True
        # Allow population by field name or alias
        allow_population_by_field_name = True
        # Validate assignments
        validate_assignment = True


class SortOrder(str, Enum):
    """Sort order enumeration - follows ISP principle"""
    ASC = "asc"
    DESC = "desc"


class AuthType(str, Enum):
    """Authentication type enumeration"""
    LOCAL = "local"
    LDAP = "ldap"
    RADIUS = "radius"
    SQL = "sql"
    USER_AUTH = "userAuth"  # From PHP code


class PasswordType(str, Enum):
    """Password type enumeration"""
    CLEARTEXT = "Cleartext-Password"  # Match PHP naming
    CRYPT = "Crypt-Password" 
    MD5 = "MD5-Password"
    SHA = "SHA-Password"
    NT = "NT-Password"
    LM = "LM-Password"


class AccountType(str, Enum):
    """Account generation type enumeration for batch operations"""
    RANDOM_USER_RANDOM_PASSWORD = "random_user_random_password"
    INCREMENTAL_USER_RANDOM_PASSWORD = "incremental_user_random_password"
    RANDOM_PINCODE_NO_PASSWORD = "random_pincode_no_password"


class OperatorType(str, Enum):
    """Operator type enumeration"""
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    READONLY = "readonly"


class AttributeOperator(str, Enum):
    """RADIUS attribute operator enumeration"""
    EQUAL = "="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    REGEX_MATCH = "=~"
    REGEX_NOT_MATCH = "!~"
    APPEND = "+="
    SET = ":="


# ============================================================================
# User Management Models (mng-*.php files)
# ============================================================================

class UserInfo(BaseUserModel):
    """Model for user profile information - covers userinfo table"""
    username: str = Field(..., min_length=1, max_length=64)
    firstname: Optional[str] = Field(None, max_length=200)
    lastname: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    workphone: Optional[str] = Field(None, max_length=200)
    homephone: Optional[str] = Field(None, max_length=200)
    mobilephone: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=200)
    state: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    zip: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    changeuserinfo: Optional[int] = Field(0, ge=0, le=1)
    portalloginpassword: Optional[str] = Field(None, max_length=128)
    enableportallogin: Optional[int] = Field(0, ge=0, le=1)
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = Field(None, max_length=128)
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = Field(None, max_length=128)

    @validator('workphone', 'homephone', 'mobilephone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\-\(\)\s]+$', v):
            raise ValueError('Invalid phone number format')
        return v


class UserBillInfo(BaseUserModel):
    """Model for user billing information - covers userbillinfo table"""
    username: str = Field(..., min_length=1, max_length=64)
    contactperson: Optional[str] = Field(None, max_length=200, alias="bi_contactperson")
    company: Optional[str] = Field(None, max_length=200, alias="bi_company")
    email: Optional[EmailStr] = Field(None, alias="bi_email")
    phone: Optional[str] = Field(None, max_length=200, alias="bi_phone")
    address: Optional[str] = Field(None, max_length=200, alias="bi_address")
    city: Optional[str] = Field(None, max_length=200, alias="bi_city")
    state: Optional[str] = Field(None, max_length=200, alias="bi_state")
    country: Optional[str] = Field(None, max_length=200, alias="bi_country")
    zip: Optional[str] = Field(None, max_length=200, alias="bi_zip")
    paymentmethod: Optional[str] = Field(None, max_length=200, alias="bi_paymentmethod")
    cash: Optional[str] = Field(None, max_length=200, alias="bi_cash")
    creditcardname: Optional[str] = Field(None, max_length=200, alias="bi_creditcardname")
    creditcardnumber: Optional[str] = Field(None, max_length=200, alias="bi_creditcardnumber")
    creditcardverification: Optional[str] = Field(None, max_length=200, alias="bi_creditcardverification")
    creditcardtype: Optional[str] = Field(None, max_length=200, alias="bi_creditcardtype")
    creditcardexp: Optional[str] = Field(None, max_length=200, alias="bi_creditcardexp")
    lead: Optional[str] = Field(None, max_length=200, alias="bi_lead")
    coupon: Optional[str] = Field(None, max_length=200, alias="bi_coupon")
    ordertaker: Optional[str] = Field(None, max_length=200, alias="bi_ordertaker")
    billstatus: Optional[str] = Field(None, max_length=200, alias="bi_billstatus")
    lastbill: Optional[date] = Field(None, alias="bi_lastbill")
    nextbill: Optional[date] = Field(None, alias="bi_nextbill")
    nextinvoicedue: Optional[date] = Field(None, alias="bi_nextinvoicedue")
    billdue: Optional[date] = Field(None, alias="bi_billdue")
    postalinvoice: Optional[str] = Field(None, max_length=200, alias="bi_postalinvoice")
    faxinvoice: Optional[str] = Field(None, max_length=200, alias="bi_faxinvoice")
    emailinvoice: Optional[str] = Field(None, max_length=200, alias="bi_emailinvoice")
    notes: Optional[str] = Field(None, alias="bi_notes")
    changeuserbillinfo: Optional[int] = Field(0, ge=0, le=1, alias="bi_changeuserbillinfo")
    batch_id: Optional[int] = None
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = Field(None, max_length=128)
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = Field(None, max_length=128)

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\-\(\)\s]+$', v):
            raise ValueError('Invalid phone number format')
        return v


class RadCheck(BaseUserModel):
    """Model for user authentication data - covers radcheck table"""
    id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=64)
    attribute: str = Field(..., max_length=64)
    op: AttributeOperator = Field(default=AttributeOperator.EQUAL)
    value: str = Field(..., max_length=253)

    @validator('attribute')
    def validate_attribute(cls, v):
        # Common RADIUS check attributes
        valid_attributes = [
            'User-Password', 'Password', 'Crypt-Password', 'MD5-Password',
            'SHA-Password', 'NT-Password', 'LM-Password', 'Auth-Type',
            'Simultaneous-Use', 'Max-Daily-Session', 'Max-Monthly-Session',
            'Expiration', 'Access-Period', 'Login-Time'
        ]
        if v not in valid_attributes:
            # Allow custom attributes but warn
            pass
        return v


class RadReply(BaseUserModel):
    """Model for user authorization attributes - covers radreply table"""
    id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=64)
    attribute: str = Field(..., max_length=64)
    op: AttributeOperator = Field(default=AttributeOperator.EQUAL)
    value: str = Field(..., max_length=253)

    @validator('attribute')
    def validate_attribute(cls, v):
        # Common RADIUS reply attributes
        valid_attributes = [
            'Framed-IP-Address', 'Framed-IP-Netmask', 'Framed-Protocol',
            'Service-Type', 'Session-Timeout', 'Idle-Timeout',
            'Acct-Interim-Interval', 'Port-Limit', 'Framed-Route',
            'Filter-Id', 'Reply-Message', 'Callback-Number'
        ]
        if v not in valid_attributes:
            # Allow custom attributes but warn
            pass
        return v


class RadUserGroup(BaseUserModel):
    """Model for user group associations - covers radusergroup table"""
    id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=64)
    groupname: str = Field(..., min_length=1, max_length=64)
    priority: int = Field(default=1, ge=0)


class User(BaseUserModel):
    """Complete user model combining all user-related data"""
    username: str = Field(..., min_length=1, max_length=64)
    password: Optional[str] = None
    auth_type: AuthType = Field(default=AuthType.LOCAL, alias="authType")
    password_type: PasswordType = Field(default=PasswordType.CLEARTEXT, alias="passwordType")
    macaddress: Optional[str] = Field(None, max_length=17)
    pincode: Optional[str] = Field(None, max_length=32)
    groups: List[str] = Field(default_factory=list)
    user_info: Optional[UserInfo] = None
    user_bill_info: Optional[UserBillInfo] = None
    dict_attributes: Dict[str, Any] = Field(default_factory=dict, alias="dictAttributes")

    @validator('macaddress')
    def validate_mac_address(cls, v):
        if v and not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', v):
            raise ValueError('Invalid MAC address format')
        return v

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9._@-]+$', v):
            raise ValueError('Username contains invalid characters')
        return v


# ============================================================================
# Batch Operation Models
# ============================================================================

class BatchHistory(BaseUserModel):
    """Model for batch history - covers batch_history table"""
    id: Optional[int] = None
    batch_name: str = Field(..., min_length=1, max_length=128)
    batch_description: Optional[str] = None
    hotspot_id: Optional[int] = None
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = Field(None, max_length=128)
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = Field(None, max_length=128)


class BatchAddUser(BaseUserModel):
    """Model for batch user addition"""
    username: str = Field(..., min_length=1, max_length=64)
    password: Optional[str] = None
    default_group: Optional[str] = None


class BatchAddRequest(BaseUserModel):
    """Model for batch add user request"""
    batch_name: str = Field(..., min_length=1, max_length=128)
    batch_description: Optional[str] = None
    hotspot_id: Optional[int] = None
    user_list: Optional[List[BatchAddUser]] = None
    # Account generation settings
    account_type: AccountType = Field(default=AccountType.RANDOM_USER_RANDOM_PASSWORD, alias="accountType")
    username_prefix: Optional[str] = None
    number: int = Field(default=4, ge=1, le=1000)
    length_pass: int = Field(default=8, ge=4, le=64)
    length_user: int = Field(default=8, ge=4, le=64)
    starting_index: int = Field(default=1000, ge=1, alias="startingIndex")
    password_type: PasswordType = Field(default=PasswordType.CLEARTEXT, alias="passwordType")
    group: Optional[str] = None
    group_priority: int = Field(default=0, ge=0)
    plan_name: Optional[str] = Field(None, alias="planName")
    # User info template
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    company: Optional[str] = None
    workphone: Optional[str] = None
    homephone: Optional[str] = None
    mobilephone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip: Optional[str] = None
    notes: Optional[str] = None
    portal_login_password: Optional[str] = Field(None, alias="portalLoginPassword")
    change_user_info: bool = Field(False, alias="changeUserInfo")
    enable_user_portal_login: bool = Field(False, alias="enableUserPortalLogin")
    # Bill info template
    user_bill_info: Optional[UserBillInfo] = None


class BatchDeleteRequest(BaseUserModel):
    """Model for batch delete user request"""
    user_list: List[str]  # List of usernames
    confirmed: bool = False


class BatchOperationResult(BaseUserModel):
    """Model for batch operation results"""
    success_count: int = 0
    error_count: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# ============================================================================
# User Search and Listing Models
# ============================================================================

class UserSearchRequest(BaseUserModel):
    """Model for user search request"""
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None
    group: Optional[str] = None


class UserListRequest(BaseUserModel):
    """Model for user list request"""
    username: Optional[str] = None
    group: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
    sort_by: Optional[str] = "username"
    sort_order: SortOrder = SortOrder.ASC


class UserListItem(BaseUserModel):
    """Model for user list item display"""
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None
    groups: List[str] = Field(default_factory=list)
    last_login: Optional[datetime] = None
    enabled: bool = True


class UserListResponse(BaseUserModel):
    """Model for user list response"""
    users: List[UserListItem]
    total_count: int
    page: int
    per_page: int
    total_pages: int


# ============================================================================
# User Import Models
# ============================================================================

class ImportSettings(BaseUserModel):
    """Model for import settings"""
    delimiter: str = Field(default=",", max_length=1)
    enclosure: str = Field(default='"', max_length=1)
    escape: str = Field(default="\\", max_length=1)
    has_header: bool = True
    default_group: Optional[str] = None
    default_password: Optional[str] = None


class ImportUserRequest(BaseUserModel):
    """Model for user import request"""
    import_file: str  # Base64 encoded file content or file path
    settings: ImportSettings


class ImportResult(BaseUserModel):
    """Model for import operation result"""
    total_processed: int = 0
    successful_imports: int = 0
    failed_imports: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# ============================================================================
# Hotspot Management Models
# ============================================================================

class Hotspot(BaseUserModel):
    """Model for hotspot definition - covers dalohotspots table"""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=128)
    mac_address: str = Field(..., max_length=17, alias="mac")
    geocode: Optional[str] = Field(None, max_length=200)
    hotspot_type: Optional[str] = Field(None, max_length=128, alias="type")
    ownername: Optional[str] = Field(None, max_length=200, alias="owner")
    managername: Optional[str] = Field(None, max_length=200, alias="manager")
    emailmanager: Optional[EmailStr] = Field(None, alias="email_manager")
    emailowner: Optional[EmailStr] = Field(None, alias="email_owner")
    address: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    phone1: Optional[str] = Field(None, max_length=200)
    phone2: Optional[str] = Field(None, max_length=200)
    companyphone: Optional[str] = Field(None, max_length=200)
    companywebsite: Optional[str] = Field(None, max_length=200)
    companyemail: Optional[EmailStr] = None
    companycontact: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)  # Keep for backward compatibility
    description: Optional[str] = None
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = Field(None, max_length=64)
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = Field(None, max_length=64)

    @validator('mac_address')
    def validate_mac_address(cls, v):
        if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', v):
            # Also allow IP addresses for some hotspot implementations
            if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', v):
                raise ValueError('Invalid MAC address or IP address format')
        return v

    @validator('phone1', 'phone2', 'companyphone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\-\(\)\s]+$', v):
            raise ValueError('Invalid phone number format')
        return v


class HotspotCreateRequest(BaseUserModel):
    """Model for hotspot creation request"""
    name: str = Field(..., min_length=1, max_length=128)
    macaddress: str = Field(..., max_length=17)  # Keep PHP naming for compatibility
    geocode: Optional[str] = Field(None, max_length=200)
    hotspot_type: Optional[str] = Field(None, max_length=128)
    ownername: Optional[str] = Field(None, max_length=200)
    managername: Optional[str] = Field(None, max_length=200)
    emailmanager: Optional[EmailStr] = None
    emailowner: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    phone1: Optional[str] = Field(None, max_length=200)
    phone2: Optional[str] = Field(None, max_length=200)
    companyphone: Optional[str] = Field(None, max_length=200)
    companywebsite: Optional[str] = Field(None, max_length=200)
    companyemail: Optional[EmailStr] = None
    companycontact: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)  # Keep for backward compatibility
    description: Optional[str] = None


class HotspotUpdateRequest(BaseUserModel):
    """Model for hotspot update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    macaddress: Optional[str] = Field(None, max_length=17)  # Keep PHP naming
    geocode: Optional[str] = Field(None, max_length=200)
    hotspot_type: Optional[str] = Field(None, max_length=128)
    ownername: Optional[str] = Field(None, max_length=200)
    managername: Optional[str] = Field(None, max_length=200)
    emailmanager: Optional[EmailStr] = None
    emailowner: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    phone1: Optional[str] = Field(None, max_length=200)
    phone2: Optional[str] = Field(None, max_length=200)
    companyphone: Optional[str] = Field(None, max_length=200)
    companywebsite: Optional[str] = Field(None, max_length=200)
    companyemail: Optional[EmailStr] = None
    companycontact: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class HotspotDeleteRequest(BaseUserModel):
    """Model for hotspot deletion request"""
    hotspot_id: int
    confirmed: bool = False


# ============================================================================
# RADIUS Attributes Management Models
# ============================================================================

class RadAttribute(BaseUserModel):
    """Model for RADIUS attribute management"""
    id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=64)
    attribute: str = Field(..., max_length=64)
    op: AttributeOperator = Field(default=AttributeOperator.EQUAL)
    value: str = Field(..., max_length=253)
    attribute_type: str = Field(default="check")  # "check" or "reply"


class RadiusDictionary(BaseUserModel):
    """Model for RADIUS dictionary attributes - covers dalodictionary table"""
    id: Optional[int] = None
    type: Optional[str] = Field(None, max_length=64)
    attribute: str = Field(..., max_length=64)
    value: Optional[str] = Field(None, max_length=64)
    format: Optional[str] = Field(None, max_length=64)
    vendor: str = Field(..., max_length=64)
    recommended_op: Optional[AttributeOperator] = Field(None, alias="RecommendedOP")
    recommended_table: Optional[str] = Field(None, max_length=32, alias="RecommendedTable")
    recommended_helper: Optional[str] = Field(None, max_length=64, alias="RecommendedHelper")
    recommended_tooltip: Optional[str] = Field(None, alias="RecommendedTooltip")

    @validator('recommended_table')
    def validate_recommended_table(cls, v):
        if v and v not in ['check', 'reply']:
            raise ValueError('recommended_table must be either "check" or "reply"')
        return v


class RadAttributeCreateRequest(BaseUserModel):
    """Model for RADIUS attribute creation request"""
    username: str = Field(..., min_length=1, max_length=64)
    attribute: str = Field(..., max_length=64)
    op: AttributeOperator = Field(default=AttributeOperator.EQUAL)
    value: str = Field(..., max_length=253)
    table: str = Field(default="check")  # "check" or "reply"


class RadiusDictionaryCreateRequest(BaseUserModel):
    """Model for RADIUS dictionary attribute creation request"""
    vendor: str = Field(..., max_length=64)
    attribute: str = Field(..., max_length=64)
    type: Optional[str] = Field(None, max_length=64)
    recommended_op: Optional[AttributeOperator] = Field(None, alias="RecommendedOP")
    recommended_table: Optional[str] = Field(None, max_length=32, alias="RecommendedTable")
    recommended_helper: Optional[str] = Field(None, max_length=64, alias="RecommendedHelper")
    recommended_tooltip: Optional[str] = Field(None, alias="RecommendedTooltip")


class RadAttributeUpdateRequest(BaseUserModel):
    """Model for RADIUS attribute update request"""
    attribute: Optional[str] = Field(None, max_length=64)
    op: Optional[AttributeOperator] = None
    value: Optional[str] = Field(None, max_length=253)


class RadAttributeSearchRequest(BaseUserModel):
    """Model for RADIUS attribute search request"""
    attribute: Optional[str] = None
    value: Optional[str] = None
    op: Optional[AttributeOperator] = None
    username: Optional[str] = None


class RadAttributeImportRequest(BaseUserModel):
    """Model for RADIUS attribute import request"""
    import_file: str  # Base64 encoded file content or file path
    delimiter: str = Field(default=",", max_length=1)


# ============================================================================
# RADIUS Resource Management Models (NAS, Realms, Proxies, IP Pools, Profiles,
# Group Check/Reply, Hunt Groups, User-Group Mapping)
# ============================================================================

class NAS(BaseUserModel):
    """Model for Network Access Server (radnas table)"""
    id: Optional[int] = None
    nasname: str = Field(..., min_length=1, max_length=128)
    shortname: Optional[str] = Field(None, max_length=64)
    type: Optional[str] = Field(None, max_length=64, alias="nastype")
    ports: Optional[int] = Field(None, ge=1, le=65535, alias="nasports")
    secret: str = Field(..., min_length=1, max_length=128, alias="nassecret")
    server: Optional[str] = Field(None, max_length=128, alias="nasvirtualserver")
    community: Optional[str] = Field(None, max_length=128, alias="nascommunity")
    description: Optional[str] = Field(None, alias="nasdescription")

    @validator('nasname')
    def validate_nasname(cls, v):
        # Allow hostname or IP
        if not re.match(r'^[A-Za-z0-9_.:-]+$', v):
            raise ValueError('Invalid NAS name format')
        return v


class NASCreateRequest(BaseUserModel):
    """Creation request for NAS"""
    nasname: str = Field(..., min_length=1, max_length=128)
    nassecret: str = Field(..., min_length=1, max_length=128)
    nastype: Optional[str] = Field(None, max_length=64)
    shortname: Optional[str] = Field(None, max_length=64)
    nasports: Optional[int] = Field(None, ge=1, le=65535)
    nasvirtualserver: Optional[str] = Field(None, max_length=128)
    nascommunity: Optional[str] = Field(None, max_length=128)
    nasdescription: Optional[str] = None

    @validator('nasname')
    def validate_nasname(cls, v):
        if not re.match(r'^[A-Za-z0-9_.:-]+$', v):
            raise ValueError('Invalid NAS name format')
        return v


class NASUpdateRequest(BaseUserModel):
    """Update request for NAS (nasname immutable key)"""
    secret: Optional[str] = Field(None, min_length=1, max_length=128)
    type: Optional[str] = Field(None, max_length=64)
    shortname: Optional[str] = Field(None, max_length=64)
    ports: Optional[int] = Field(None, ge=1, le=65535)
    server: Optional[str] = Field(None, max_length=128)
    community: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None


class Realm(BaseUserModel):
    """Model for Realm (dalorealms table)"""
    id: Optional[int] = None
    realmname: str = Field(..., min_length=1, max_length=128)
    type: Optional[str] = Field(None, max_length=64)
    authhost: Optional[str] = Field(None, max_length=128)
    accthost: Optional[str] = Field(None, max_length=128)
    secret: Optional[str] = Field(None, max_length=128)
    ldflag: Optional[str] = Field(None, max_length=64)
    nostrip: bool = Field(False)
    hints: Optional[str] = Field(None, max_length=128)
    notrealm: Optional[str] = Field(None, max_length=128)
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = Field(None, max_length=128)
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = Field(None, max_length=128)


class RealmCreateRequest(BaseUserModel):
    """Creation request for Realm"""
    realmname: str = Field(..., min_length=1, max_length=128)
    type: Optional[str] = Field(None, max_length=64)
    authhost: Optional[str] = Field(None, max_length=128)
    accthost: Optional[str] = Field(None, max_length=128)
    secret: Optional[str] = Field(None, max_length=128)
    ldflag: Optional[str] = Field(None, max_length=64)
    nostrip: bool = Field(False)
    hints: Optional[str] = Field(None, max_length=128)
    notrealm: Optional[str] = Field(None, max_length=128)


class RealmUpdateRequest(BaseUserModel):
    """Update request for Realm"""
    type: Optional[str] = Field(None, max_length=64)
    authhost: Optional[str] = Field(None, max_length=128)
    accthost: Optional[str] = Field(None, max_length=128)
    secret: Optional[str] = Field(None, max_length=128)
    ldflag: Optional[str] = Field(None, max_length=64)
    nostrip: Optional[bool] = None
    hints: Optional[str] = Field(None, max_length=128)
    notrealm: Optional[str] = Field(None, max_length=128)


class ProxyServer(BaseUserModel):
    """Model for Proxy (daloproxys table)"""
    id: Optional[int] = None
    proxyname: str = Field(..., min_length=1, max_length=128)
    retry_delay: Optional[int] = Field(None, ge=0)
    retry_count: Optional[int] = Field(None, ge=0)
    dead_time: Optional[int] = Field(None, ge=0)
    default_fallback: Optional[int] = Field(None, ge=0)
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = Field(None, max_length=128)
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = Field(None, max_length=128)


class ProxyCreateRequest(BaseUserModel):
    """Creation request for Proxy"""
    proxyname: str = Field(..., min_length=1, max_length=128)
    retry_delay: Optional[int] = Field(None, ge=0)
    retry_count: Optional[int] = Field(None, ge=0)
    dead_time: Optional[int] = Field(None, ge=0)
    default_fallback: Optional[int] = Field(None, ge=0)


class ProxyUpdateRequest(BaseUserModel):
    """Update request for Proxy"""
    retry_delay: Optional[int] = Field(None, ge=0)
    retry_count: Optional[int] = Field(None, ge=0)
    dead_time: Optional[int] = Field(None, ge=0)
    default_fallback: Optional[int] = Field(None, ge=0)


class IPPoolEntry(BaseUserModel):
    """Model for IP Pool entry (radippool table)"""
    id: Optional[int] = None
    pool_name: str = Field(..., min_length=1, max_length=128)
    framedipaddress: IPv4Address


class IPPoolCreateRequest(BaseUserModel):
    """Creation request for IP Pool entry"""
    pool_name: str = Field(..., min_length=1, max_length=128)
    framedipaddress: IPv4Address


class Profile(BaseUserModel):
    """Model for Profile (logical grouping of attributes, backed by group entries)"""
    profile_name: str = Field(..., min_length=1, max_length=128, alias="profile")
    attributes: List[RadAttribute] = Field(default_factory=list)


class ProfileCreateRequest(BaseUserModel):
    """Creation request for Profile"""
    profile: str = Field(..., min_length=1, max_length=128)
    attributes: List[RadAttribute] = Field(default_factory=list)


class GroupCheckItem(BaseUserModel):
    """Model for radgroupcheck entry"""
    id: Optional[int] = None
    groupname: str = Field(..., min_length=1, max_length=64)
    attribute: str = Field(..., max_length=64)
    op: AttributeOperator = Field(default=AttributeOperator.EQUAL)
    value: str = Field(..., max_length=253)


class GroupReplyItem(BaseUserModel):
    """Model for radgroupreply entry"""
    id: Optional[int] = None
    groupname: str = Field(..., min_length=1, max_length=64)
    attribute: str = Field(..., max_length=64)
    op: AttributeOperator = Field(default=AttributeOperator.EQUAL)
    value: str = Field(..., max_length=253)


class GroupAttributesCreateRequest(BaseUserModel):
    """Generic creation request for group attributes (check or reply)"""
    groupname: str = Field(..., min_length=1, max_length=64)
    attributes: List[RadAttribute] = Field(..., min_length=1)
    table: str = Field(..., regex=r'^(check|reply)$')


class HuntGroupEntry(BaseUserModel):
    """Model for huntgroup entry (radhuntgroup table)"""
    id: Optional[int] = None
    groupname: str = Field(..., min_length=1, max_length=64)
    nasipaddress: IPv4Address
    nasportid: Optional[int] = Field(0, ge=0)


class HuntGroupCreateRequest(BaseUserModel):
    """Creation request for huntgroup entry"""
    groupname: str = Field(..., min_length=1, max_length=64)
    nasipaddress: IPv4Address
    nasportid: Optional[int] = Field(0, ge=0)


class UserGroupMappingCreateRequest(BaseUserModel):
    """Creation request for radusergroup mapping"""
    username: str = Field(..., min_length=1, max_length=64)
    groupname: str = Field(..., min_length=1, max_length=64, alias="group")
    priority: int = Field(0, ge=0)


# ============================================================================
# Quick User Creation Models
# ============================================================================

class QuickUserCreateRequest(BaseUserModel):
    """Model for quick user creation"""
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)


class QuickUserCreateResponse(BaseUserModel):
    """Model for quick user creation response"""
    username: str
    password: str
    success: bool
    message: Optional[str] = None


# ============================================================================
# Operation Result Models
# ============================================================================

class OperationResult(BaseUserModel):
    """Generic operation result model"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class UserCreateRequest(BaseUserModel):
    """Model for comprehensive user creation request"""
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)
    auth_type: AuthType = Field(default=AuthType.LOCAL, alias="authType")
    password_type: PasswordType = Field(default=PasswordType.CLEARTEXT, alias="passwordType")
    macaddress: Optional[str] = Field(None, max_length=17)
    pincode: Optional[str] = Field(None, max_length=32)
    groups: List[str] = Field(default_factory=list)
    firstname: Optional[str] = Field(None, max_length=200)
    lastname: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    workphone: Optional[str] = Field(None, max_length=200)
    homephone: Optional[str] = Field(None, max_length=200)
    mobilephone: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=200)
    state: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    zip: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    portal_login_password: Optional[str] = Field(None, max_length=128, alias="portalLoginPassword")
    change_user_info: bool = Field(False, alias="changeUserInfo")
    enable_user_portal_login: bool = Field(False, alias="enableUserPortalLogin")
    dict_attributes: Dict[str, Any] = Field(default_factory=dict, alias="dictAttributes")
    # Include billing info fields directly for easier processing
    user_bill_info: Optional[UserBillInfo] = None


class UserUpdateRequest(BaseUserModel):
    """Model for comprehensive user update request"""
    password: Optional[str] = None
    auth_type: Optional[AuthType] = Field(None, alias="authType")
    password_type: Optional[PasswordType] = Field(None, alias="passwordType")
    macaddress: Optional[str] = Field(None, max_length=17)
    pincode: Optional[str] = Field(None, max_length=32)
    groups: Optional[List[str]] = None
    firstname: Optional[str] = Field(None, max_length=200)
    lastname: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    workphone: Optional[str] = Field(None, max_length=200)
    homephone: Optional[str] = Field(None, max_length=200)
    mobilephone: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=200)
    state: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    zip: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    portal_login_password: Optional[str] = Field(None, max_length=128, alias="portalLoginPassword")
    change_user_info: Optional[bool] = Field(None, alias="changeUserInfo")
    enable_user_portal_login: Optional[bool] = Field(None, alias="enableUserPortalLogin")
    dict_attributes: Optional[Dict[str, Any]] = Field(None, alias="dictAttributes")
    user_bill_info: Optional[UserBillInfo] = None


class UserDeleteRequest(BaseUserModel):
    """Model for user deletion request"""
    username: str = Field(..., min_length=1, max_length=64)
    confirmed: bool = False


# ============================================================================
# Response Models for API endpoints
# ============================================================================

class UserResponse(BaseUserModel):
    """Model for user API response"""
    username: str
    auth_type: AuthType
    user_info: Optional[UserInfo] = None
    groups: List[str] = Field(default_factory=list)
    attributes: List[RadAttribute] = Field(default_factory=list)
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None


class HotspotListResponse(BaseUserModel):
    """Model for hotspot list response"""
    hotspots: List[Hotspot]
    total_count: int


class RadAttributeListResponse(BaseUserModel):
    """Model for RADIUS attribute list response"""
    attributes: List[RadAttribute]
    total_count: int


# ============================================================================
# Validation Functions
# ============================================================================

def validate_username_format(username: str) -> bool:
    """Validate username format according to RADIUS standards"""
    if not username or len(username) == 0:
        return False
    if len(username) > 64:
        return False
    if not re.match(r'^[a-zA-Z0-9._@-]+$', username):
        return False
    return True


def validate_password_strength(password: str, min_length: int = 8) -> List[str]:
    """Validate password strength and return list of issues"""
    issues = []
    
    if len(password) < min_length:
        issues.append(f"Password must be at least {min_length} characters long")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    
    return issues


def generate_radius_attributes(user_data: Dict[str, Any]) -> List[RadAttribute]:
    """Generate RADIUS attributes from user data"""
    attributes = []
    
    # Add check attributes
    if 'password' in user_data:
        attributes.append(RadAttribute(
            username=user_data['username'],
            attribute='User-Password',
            op=AttributeOperator.EQUAL,
            value=user_data['password'],
            attribute_type='check'
        ))
    
    # Add reply attributes based on user settings
    if 'session_timeout' in user_data:
        attributes.append(RadAttribute(
            username=user_data['username'],
            attribute='Session-Timeout',
            op=AttributeOperator.EQUAL,
            value=str(user_data['session_timeout']),
            attribute_type='reply'
        ))
    
    return attributes


# ============================================================================
# Export all models for easy importing
# ============================================================================

__all__ = [
    # Enums
    'SortOrder',
    'AuthType', 
    'PasswordType',
    'AccountType',
    'OperatorType',
    'AttributeOperator',
    
    # Base Models
    'BaseUserModel',
    
    # Core User Models
    'UserInfo',
    'UserBillInfo',
    'RadCheck',
    'RadReply',
    'RadUserGroup',
    'User',
    
    # Batch Operation Models
    'BatchHistory',
    'BatchAddUser',
    'BatchAddRequest',
    'BatchDeleteRequest',
    'BatchOperationResult',
    
    # Search and Listing Models
    'UserSearchRequest',
    'UserListRequest',
    'UserListItem',
    'UserListResponse',
    
    # Import Models
    'ImportSettings',
    'ImportUserRequest',
    'ImportResult',
    
    # Hotspot Models
    'Hotspot',
    'HotspotCreateRequest',
    'HotspotUpdateRequest',
    'HotspotDeleteRequest',
    
    # RADIUS Attribute Models
    'RadAttribute',
    'RadiusDictionary',
    'RadAttributeCreateRequest',
    'RadiusDictionaryCreateRequest',
    'RadAttributeUpdateRequest',
    'RadAttributeSearchRequest',
    'RadAttributeImportRequest',

    # RADIUS Resource Management Models
    'NAS', 'NASCreateRequest', 'NASUpdateRequest',
    'Realm', 'RealmCreateRequest', 'RealmUpdateRequest',
    'ProxyServer', 'ProxyCreateRequest', 'ProxyUpdateRequest',
    'IPPoolEntry', 'IPPoolCreateRequest',
    'Profile', 'ProfileCreateRequest',
    'GroupCheckItem', 'GroupReplyItem', 'GroupAttributesCreateRequest',
    'HuntGroupEntry', 'HuntGroupCreateRequest',
    'UserGroupMappingCreateRequest',
    
    # Quick User Models
    'QuickUserCreateRequest',
    'QuickUserCreateResponse',
    
    # Operation Result Models
    'OperationResult',
    'UserCreateRequest',
    'UserUpdateRequest',
    'UserDeleteRequest',
    
    # Response Models
    'UserResponse',
    'HotspotListResponse',
    'RadAttributeListResponse',
    
    # Validation Functions
    'validate_username_format',
    'validate_password_strength',
    'generate_radius_attributes',
]
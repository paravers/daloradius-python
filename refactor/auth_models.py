"""
Authentication & Authorization Module Data Models

Covers:
- Operator login (login.php, dologin.php implied)
- Session validation (library/checklogin.php)
- Authentication backends (local SQL, LDAP, RADIUS proxy)
- Password management
- Authorization attribute evaluation (radcheck/radreply style abstraction)
- Post authentication logging (radpostauth equivalent)
- Access decision pipeline

NOTE: radpostauth table structure inferred (common FreeRADIUS schema):
  radpostauth (id, username, pass, reply, authdate)
If repository specifics differ, adjust PostAuthLog model accordingly.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from enum import Enum
from ipaddress import IPv4Address
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr
import re


class BaseAuthModel(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True


# ===================== Enums =====================
class AuthBackendType(str, Enum):
    LOCAL_SQL = "local_sql"
    LDAP = "ldap"
    RADIUS_PROXY = "radius_proxy"
    EXTERNAL = "external"  # placeholder for plugins

class PasswordHashAlgo(str, Enum):
    CLEARTEXT = "cleartext"
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    BCRYPT = "bcrypt"

class AuthStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    LOCKED = "locked"
    EXPIRED = "expired"

class TokenType(str, Enum):
    SESSION = "session"
    API = "api"
    REFRESH = "refresh"

# ===================== Core Auth / Session Models =====================
class CredentialInput(BaseAuthModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=256)
    location: Optional[str] = Field(None, max_length=64)
    csrf_token: Optional[str] = Field(None, alias="csrfToken")

    @validator('username')
    def username_chars(cls, v):
        if not re.match(r'^[A-Za-z0-9._@-]+$', v):
            raise ValueError('Invalid username characters')
        return v

class LoginRequest(CredentialInput):
    backend_hint: Optional[AuthBackendType] = Field(None, alias="backend")

class LoginResponse(BaseAuthModel):
    status: AuthStatus
    message: Optional[str] = None
    session_id: Optional[str] = Field(None, alias="sessionId")
    token: Optional[str] = None
    token_type: Optional[TokenType] = Field(None, alias="tokenType")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")

class SessionInfo(BaseAuthModel):
    session_id: str = Field(..., alias="sessionId")
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    last_activity: datetime = Field(default_factory=datetime.utcnow, alias="lastActivity")
    ip_address: Optional[IPv4Address] = Field(None, alias="ipAddress")
    user_agent: Optional[str] = Field(None, max_length=256, alias="userAgent")
    location: Optional[str] = None
    valid: bool = True

    @property
    def age_seconds(self) -> int:
        return int((datetime.utcnow() - self.created_at).total_seconds())

# ===================== Password & Validation =====================
class PasswordChangeRequest(BaseAuthModel):
    username: str
    old_password: str = Field(..., alias="oldPassword")
    new_password: str = Field(..., alias="newPassword")

class PasswordValidationResult(BaseAuthModel):
    valid: bool
    issues: List[str] = Field(default_factory=list)

# ===================== Backend Configurations =====================
class LDAPConfig(BaseAuthModel):
    enabled: bool = True
    uri: str = Field(..., max_length=256)
    base_dn: str = Field(..., max_length=256, alias="baseDN")
    bind_dn: Optional[str] = Field(None, max_length=256, alias="bindDN")
    bind_password: Optional[str] = Field(None, max_length=256, alias="bindPassword")
    user_filter: str = Field("(uid={username})", max_length=256, alias="userFilter")
    use_start_tls: bool = Field(False, alias="useStartTLS")
    timeout_seconds: int = Field(5, ge=1, le=60, alias="timeoutSeconds")

class RadiusProxyConfig(BaseAuthModel):
    enabled: bool = False
    server: Optional[str] = Field(None, max_length=128)
    secret: Optional[str] = Field(None, max_length=128)
    auth_port: int = Field(1812, ge=1, le=65535, alias="authPort")
    acct_port: int = Field(1813, ge=1, le=65535, alias="acctPort")
    timeout_seconds: int = Field(5, ge=1, le=60, alias="timeoutSeconds")
    retries: int = Field(3, ge=0, le=10)

class SqlAuthConfig(BaseAuthModel):
    enabled: bool = True
    user_table: str = Field("operators", max_length=64, alias="userTable")
    username_column: str = Field("username", max_length=64, alias="usernameColumn")
    password_column: str = Field("password", max_length=64, alias="passwordColumn")
    password_hash_algo: PasswordHashAlgo = Field(PasswordHashAlgo.CLEARTEXT, alias="passwordHashAlgo")

# ===================== Authorization & Attributes =====================
class AuthorizationAttribute(BaseAuthModel):
    name: str = Field(..., max_length=64)
    op: str = Field("=", max_length=4)
    value: str = Field(..., max_length=253)
    table: str = Field("check", regex=r"^(check|reply)$")

class AccessRequest(BaseAuthModel):
    username: str
    password: Optional[str] = None
    attributes: List[AuthorizationAttribute] = Field(default_factory=list)
    backend_chain: List[AuthBackendType] = Field(default_factory=list, alias="backendChain")
    ip_address: Optional[IPv4Address] = Field(None, alias="ipAddress")
    nas_id: Optional[str] = Field(None, max_length=64, alias="nasId")

class AccessDecision(BaseAuthModel):
    username: str
    status: AuthStatus
    decided_at: datetime = Field(default_factory=datetime.utcnow, alias="decidedAt")
    backend_used: Optional[AuthBackendType] = Field(None, alias="backendUsed")
    message: Optional[str] = None
    reply_attributes: List[AuthorizationAttribute] = Field(default_factory=list, alias="replyAttributes")

# ===================== Post Authentication & Accounting =====================
class PostAuthLog(BaseAuthModel):
    id: Optional[int] = None
    username: str
    password: Optional[str] = None  # stored if configured (may be obfuscated)
    reply: Optional[str] = None
    authdate: datetime = Field(default_factory=datetime.utcnow)
    status: Optional[AuthStatus] = None
    nas_ip_address: Optional[IPv4Address] = Field(None, alias="nasIpAddress")

class AccountingRecord(BaseAuthModel):
    username: str
    session_id: str = Field(..., alias="sessionId")
    acct_start_time: Optional[datetime] = Field(None, alias="acctStartTime")
    acct_stop_time: Optional[datetime] = Field(None, alias="acctStopTime")
    session_time: Optional[int] = Field(None, ge=0, alias="sessionTime")
    input_octets: Optional[int] = Field(None, ge=0, alias="inputOctets")
    output_octets: Optional[int] = Field(None, ge=0, alias="outputOctets")
    terminate_cause: Optional[str] = Field(None, max_length=64, alias="terminateCause")

# ===================== Aggregated Config Snapshot =====================
class AuthBackendConfig(BaseAuthModel):
    sql: Optional[SqlAuthConfig] = None
    ldap: Optional[LDAPConfig] = None
    radius_proxy: Optional[RadiusProxyConfig] = Field(None, alias="radiusProxy")

# ===================== Exports =====================
__all__ = [
    # Enums
    'AuthBackendType','PasswordHashAlgo','AuthStatus','TokenType',
    # Base
    'BaseAuthModel',
    # Core
    'CredentialInput','LoginRequest','LoginResponse','SessionInfo',
    'PasswordChangeRequest','PasswordValidationResult',
    # Backend Config
    'LDAPConfig','RadiusProxyConfig','SqlAuthConfig','AuthBackendConfig',
    # Authorization
    'AuthorizationAttribute','AccessRequest','AccessDecision',
    # Logs & Accounting
    'PostAuthLog','AccountingRecord',
]

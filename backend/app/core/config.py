"""
Core Application Configuration

This module contains all application settings, database configuration,
and environment-specific configurations.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """

    # Application Info
    PROJECT_NAME: str = "daloRADIUS Modern API"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "Modern FastAPI-based RADIUS management system"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080"
    ]

    # Database Configuration
    DATABASE_SCHEME: str = "postgresql+asyncpg"
    DATABASE_USER: str = "daloradius"
    DATABASE_PASSWORD: str = "daloradius123"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_NAME: str = "daloradius"
    DATABASE_URL: Optional[str] = None

    # Legacy MySQL support (for migration phase)
    MYSQL_USER: str = "radius"
    MYSQL_PASSWORD: str = "radpass"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DATABASE: str = "radius"

    # Connection Pool Settings
    DATABASE_POOL_SIZE: int = 20
    DATABASE_POOL_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_PRE_PING: bool = True

    # Redis Configuration (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "app.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Email Configuration (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # File Upload
    UPLOAD_FOLDER: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ['.csv', '.txt', '.json', '.xlsx']

    # RADIUS Specific Settings
    RADIUS_SECRET: str = "testing123"
    RADIUS_DEFAULT_AUTH_PORT: int = 1812
    RADIUS_DEFAULT_ACCT_PORT: int = 1813
    RADIUS_TIMEOUT: int = 5
    RADIUS_RETRIES: int = 3

    # Billing Settings
    BILLING_CURRENCY: str = "USD"
    BILLING_DECIMAL_PLACES: int = 2
    BILLING_TAX_RATE: float = 0.0

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100

    # Monitoring & Health Checks
    HEALTH_CHECK_TIMEOUT: int = 30
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """
        Construct database URL from individual components
        """
        if isinstance(v, str):
            return v

        scheme = values.get("DATABASE_SCHEME") or "postgresql"
        user = values.get("DATABASE_USER") or ""
        password = values.get("DATABASE_PASSWORD") or ""
        host = values.get("DATABASE_HOST") or "localhost"
        port = values.get("DATABASE_PORT") or "5432"
        db_name = values.get("DATABASE_NAME") or ""

        return f"{scheme}://{user}:{password}@{host}:{port}/{db_name}"

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_cors_origins(cls, v: str) -> List[str]:
        """
        Parse comma-separated CORS origins
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def mysql_url(self) -> str:
        """
        Legacy MySQL connection URL for migration purposes
        """
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.ENVIRONMENT.lower() == "testing"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()

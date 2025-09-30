"""
Database Session Management

This module handles SQLAlchemy async database sessions and connections
for the daloRADIUS application.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from typing import AsyncGenerator

from .base import Base


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://daloradius:daloradius123@localhost:5432/daloradius"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    poolclass=NullPool,  # Use NullPool for async operations
    pool_pre_ping=True,  # Verify connections before use
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session.

    This function is typically used with FastAPI's dependency injection system.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables.

    This is typically done through Alembic migrations,
    but can be used for testing or initial setup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Drop all database tables.

    Warning: This will delete all data!
    Should only be used in development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class DatabaseManager:
    """
    Database manager for handling connections and transactions
    """

    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal

    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        return self.session_factory()

    async def close(self):
        """Close the database engine"""
        await self.engine.dispose()

    async def health_check(self) -> bool:
        """
        Check database connectivity

        Returns:
            bool: True if database is accessible, False otherwise
        """
        try:
            async with AsyncSessionLocal() as session:
                await session.execute("SELECT 1")
                return True
        except Exception:
            return False


# Global database manager instance
db_manager = DatabaseManager()

# Alias for FastAPI dependency injection
get_db = get_async_session

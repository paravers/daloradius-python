"""
Test script to verify Repository layer functionality

This script tests the basic CRUD operations using our repository pattern
and validates that the database connection and models are working correctly.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository, OperatorRepository
from app.schemas.user import UserCreate, OperatorCreate


async def test_user_repository():
    """Test user repository operations"""
    print("Testing User Repository...")
    
    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        
        # Test user creation
        from app.schemas.user import UserCreate
        user_data = UserCreate(
            username="testuser001",
            password="testpassword123",  # This will be handled by schema
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_active=True
        )
        
        try:
            # Create user
            user = await user_repo.create(user_data)
            print(f"✓ Created user: {user.username} (ID: {user.id})")
            
            # Get user by username
            found_user = await user_repo.get_by_username("testuser001")
            assert found_user is not None
            print(f"✓ Found user by username: {found_user.username}")
            
            # Test authentication
            auth_user = await user_repo.authenticate("testuser001", "testpassword123")
            assert auth_user is not None
            print(f"✓ User authentication successful")
            
            # Test failed authentication
            no_auth = await user_repo.authenticate("testuser001", "wrongpassword")
            assert no_auth is None
            print(f"✓ Failed authentication handled correctly")
            
            # Get user count
            count = await user_repo.count()
            print(f"✓ Total users in database: {count}")
            
            # Clean up
            await user_repo.delete(user.id)
            print(f"✓ Deleted test user")
            
        except Exception as e:
            print(f"✗ Error in user repository test: {e}")
            raise


async def test_operator_repository():
    """Test operator repository operations"""
    print("\nTesting Operator Repository...")
    
    async with AsyncSessionLocal() as db:
        operator_repo = OperatorRepository(db)
        
        # Test operator creation
        operator_data = OperatorCreate(
            username="testoperator",
            password="operatorpass123",
            fullname="Test Operator",
            email="operator@example.com",
            is_active=True
        )
        
        try:
            # Create operator
            operator = await operator_repo.create(operator_data)
            print(f"✓ Created operator: {operator.username} (ID: {operator.id})")
            
            # Test authentication
            auth_operator = await operator_repo.authenticate("testoperator", "operatorpass123")
            assert auth_operator is not None
            print(f"✓ Operator authentication successful")
            
            # Clean up
            await operator_repo.delete(operator.id)
            print(f"✓ Deleted test operator")
            
        except Exception as e:
            print(f"✗ Error in operator repository test: {e}")
            raise


async def test_basic_queries():
    """Test basic database queries"""
    print("\nTesting Basic Database Queries...")
    
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import text
            # Test table existence
            result = await db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            table_names = [row[0] for row in tables]
            print(f"✓ Found {len(table_names)} tables: {', '.join(table_names)}")
            
            # Test users table structure
            result = await db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            print(f"✓ Users table has {len(columns)} columns")
            
        except Exception as e:
            print(f"✗ Error in basic queries test: {e}")
            raise


async def test_database_connection():
    """Test basic database connectivity"""
    print("Testing Database Connection...")
    
    try:
        async with AsyncSessionLocal() as db:
            # Simple query to test connection
            from sqlalchemy import text
            result = await db.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Database connection successful")
            print(f"✓ PostgreSQL version: {version}")
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        raise


async def main():
    """Main test runner"""
    print("="*60)
    print("daloRADIUS Repository Layer Test Suite")
    print("="*60)
    
    try:
        await test_database_connection()
        await test_basic_queries()
        await test_user_repository()
        await test_operator_repository()
        
        print("\n" + "="*60)
        print("✓ All tests passed successfully!")
        print("✓ Repository layer is working correctly")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
"""Fix radacct IPv6 fields and operators fields

Revision ID: 002_fix_ipv6_operators
Revises: 001_initial
Create Date: 2025-09-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_fix_ipv6_operators'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing IPv6 fields to radacct table and extend operators table"""
    
    # Check if columns exist before adding them
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    radacct_columns = [col['name'] for col in inspector.get_columns('radacct')]
    operators_columns = [col['name'] for col in inspector.get_columns('operators')]
    
    # 1. Add IPv6 and missing fields to radacct table (only if they don't exist)
    if 'groupname' not in radacct_columns:
        op.add_column('radacct', sa.Column('groupname', sa.String(length=64), nullable=True))
    if 'framedipv6address' not in radacct_columns:
        op.add_column('radacct', sa.Column('framedipv6address', sa.String(length=45), nullable=True))
    if 'framedipv6prefix' not in radacct_columns:
        op.add_column('radacct', sa.Column('framedipv6prefix', sa.String(length=45), nullable=True))
    if 'framedinterfaceid' not in radacct_columns:
        op.add_column('radacct', sa.Column('framedinterfaceid', sa.String(length=44), nullable=True))
    if 'delegatedipv6prefix' not in radacct_columns:
        op.add_column('radacct', sa.Column('delegatedipv6prefix', sa.String(length=45), nullable=True))
    if 'class' not in radacct_columns:
        op.add_column('radacct', sa.Column('class', sa.String(length=64), nullable=True))
    
    # 2. Add missing fields to operators table (only if they don't exist)
    if 'firstname' not in operators_columns:
        op.add_column('operators', sa.Column('firstname', sa.String(length=32), nullable=True))
    if 'lastname' not in operators_columns:
        op.add_column('operators', sa.Column('lastname', sa.String(length=32), nullable=True))
    if 'title' not in operators_columns:
        op.add_column('operators', sa.Column('title', sa.String(length=32), nullable=True))
    if 'company' not in operators_columns:
        op.add_column('operators', sa.Column('company', sa.String(length=32), nullable=True))
    if 'phone1' not in operators_columns:
        op.add_column('operators', sa.Column('phone1', sa.String(length=32), nullable=True))
    if 'phone2' not in operators_columns:
        op.add_column('operators', sa.Column('phone2', sa.String(length=32), nullable=True))
    if 'email1' not in operators_columns:
        op.add_column('operators', sa.Column('email1', sa.String(length=32), nullable=True))
    if 'email2' not in operators_columns:
        op.add_column('operators', sa.Column('email2', sa.String(length=32), nullable=True))
    if 'messenger1' not in operators_columns:
        op.add_column('operators', sa.Column('messenger1', sa.String(length=32), nullable=True))
    if 'messenger2' not in operators_columns:
        op.add_column('operators', sa.Column('messenger2', sa.String(length=32), nullable=True))
    if 'notes' not in operators_columns:
        op.add_column('operators', sa.Column('notes', sa.String(length=128), nullable=True))
    
    # 3. Add indexes for new radacct IPv6 fields (check if they exist first)
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('radacct')]
    
    if 'idx_radacct_groupname' not in existing_indexes and 'groupname' in [col['name'] for col in inspector.get_columns('radacct')]:
        op.create_index('idx_radacct_groupname', 'radacct', ['groupname'])
    if 'idx_radacct_framedipv6address' not in existing_indexes and 'framedipv6address' in [col['name'] for col in inspector.get_columns('radacct')]:
        op.create_index('idx_radacct_framedipv6address', 'radacct', ['framedipv6address'])
    if 'idx_radacct_framedipv6prefix' not in existing_indexes and 'framedipv6prefix' in [col['name'] for col in inspector.get_columns('radacct')]:
        op.create_index('idx_radacct_framedipv6prefix', 'radacct', ['framedipv6prefix'])
    if 'idx_radacct_framedinterfaceid' not in existing_indexes and 'framedinterfaceid' in [col['name'] for col in inspector.get_columns('radacct')]:
        op.create_index('idx_radacct_framedinterfaceid', 'radacct', ['framedinterfaceid'])
    if 'idx_radacct_delegatedipv6prefix' not in existing_indexes and 'delegatedipv6prefix' in [col['name'] for col in inspector.get_columns('radacct')]:
        op.create_index('idx_radacct_delegatedipv6prefix', 'radacct', ['delegatedipv6prefix'])
    
    # 4. Add bulk close index for performance (MySQL/MariaDB style)
    if 'idx_radacct_bulk_close' not in existing_indexes:
        op.create_index('idx_radacct_bulk_close', 'radacct', ['acctstoptime', 'nasipaddress', 'acctstarttime'])


def downgrade() -> None:
    """Remove the added fields and indexes"""
    
    # Remove indexes first
    op.drop_index('idx_radacct_bulk_close', 'radacct')
    op.drop_index('idx_radacct_delegatedipv6prefix', 'radacct')
    op.drop_index('idx_radacct_framedinterfaceid', 'radacct')
    op.drop_index('idx_radacct_framedipv6prefix', 'radacct')
    op.drop_index('idx_radacct_framedipv6address', 'radacct')
    op.drop_index('idx_radacct_groupname', 'radacct')
    
    # Remove operators fields
    op.drop_column('operators', 'notes')
    op.drop_column('operators', 'messenger2')
    op.drop_column('operators', 'messenger1')
    op.drop_column('operators', 'email2')
    op.drop_column('operators', 'email1')
    op.drop_column('operators', 'phone2')
    op.drop_column('operators', 'phone1')
    op.drop_column('operators', 'company')
    op.drop_column('operators', 'title')
    op.drop_column('operators', 'lastname')
    op.drop_column('operators', 'firstname')
    
    # Remove radacct fields
    op.drop_column('radacct', 'acctauthentic')
    op.drop_column('radacct', 'acctinterval')
    op.drop_column('radacct', 'class')
    op.drop_column('radacct', 'delegatedipv6prefix')
    op.drop_column('radacct', 'framedinterfaceid')
    op.drop_column('radacct', 'framedipv6prefix')
    op.drop_column('radacct', 'framedipv6address')
    op.drop_column('radacct', 'groupname')
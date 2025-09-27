"""Create RADIUS group management tables

Revision ID: 003_radius_groups
Revises: 002_fix_ipv6_operators
Create Date: 2025-09-27 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_radius_groups'
down_revision = '002_fix_ipv6_operators'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create RADIUS group management tables"""
    
    # Create radgroupcheck table
    op.create_table('radgroupcheck',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('groupname', sa.String(length=64), nullable=False),
        sa.Column('attribute', sa.String(length=64), nullable=False),
        sa.Column('op', sa.String(length=2), nullable=False, default='=='),
        sa.Column('value', sa.String(length=253), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_radgroupcheck_groupname', 'radgroupcheck', ['groupname'])
    op.create_index('idx_radgroupcheck_groupname_attribute', 'radgroupcheck', ['groupname', 'attribute'])

    # Create radgroupreply table
    op.create_table('radgroupreply',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('groupname', sa.String(length=64), nullable=False),
        sa.Column('attribute', sa.String(length=64), nullable=False),
        sa.Column('op', sa.String(length=2), nullable=False, default='='),
        sa.Column('value', sa.String(length=253), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_radgroupreply_groupname', 'radgroupreply', ['groupname'])
    op.create_index('idx_radgroupreply_groupname_attribute', 'radgroupreply', ['groupname', 'attribute'])

    # Create radpostauth table
    op.create_table('radpostauth',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('pass', sa.String(length=64), nullable=False),
        sa.Column('reply', sa.String(length=32), nullable=False),
        sa.Column('authdate', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('class', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_radpostauth_username', 'radpostauth', ['username'])
    op.create_index('idx_radpostauth_authdate', 'radpostauth', ['authdate'])

    # Create nasreload table
    op.create_table('nasreload',
        sa.Column('nasipaddress', postgresql.INET(), nullable=False),
        sa.Column('reloadtime', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('nasipaddress')
    )

    # Create radippool table
    op.create_table('radippool',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('pool_name', sa.String(length=30), nullable=False),
        sa.Column('framedipaddress', postgresql.INET(), nullable=False),
        sa.Column('nasipaddress', postgresql.INET(), nullable=False),
        sa.Column('calledstationid', sa.String(length=30), nullable=True),
        sa.Column('callingstationid', sa.String(length=30), nullable=True),
        sa.Column('expiry_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('pool_key', sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_radippool_pool_name', 'radippool', ['pool_name'])
    op.create_index('idx_radippool_framedipaddress', 'radippool', ['framedipaddress'])
    op.create_index('idx_radippool_nasipaddress', 'radippool', ['nasipaddress'])


def downgrade() -> None:
    """Drop RADIUS group management tables"""
    
    op.drop_table('radippool')
    op.drop_table('nasreload')
    op.drop_table('radpostauth')
    op.drop_table('radgroupreply')
    op.drop_table('radgroupcheck')
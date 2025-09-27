"""Initial migration - Create daloRADIUS tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-09-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial daloRADIUS tables"""
    
    # Create operators table
    op.create_table('operators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('fullname', sa.String(length=200), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('department', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('permissions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=128), nullable=True),
        sa.Column('updated_by', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_operators_username', 'operators', ['username'])
    op.create_index('idx_operators_active', 'operators', ['is_active'])

    # Create users table (new modern table)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('auth_type', sa.Enum('LOCAL', 'LDAP', 'RADIUS', 'SQL', name='authtype'), nullable=False, default='LOCAL'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'EXPIRED', name='userstatus'), nullable=False, default='ACTIVE'),
        sa.Column('first_name', sa.String(length=200), nullable=True),
        sa.Column('last_name', sa.String(length=200), nullable=True),
        sa.Column('department', sa.String(length=200), nullable=True),
        sa.Column('company', sa.String(length=200), nullable=True),
        sa.Column('work_phone', sa.String(length=200), nullable=True),
        sa.Column('home_phone', sa.String(length=200), nullable=True),
        sa.Column('mobile_phone', sa.String(length=200), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=200), nullable=True),
        sa.Column('state', sa.String(length=200), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('zip_code', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('mac_address', sa.String(length=17), nullable=True),
        sa.Column('pin_code', sa.String(length=32), nullable=True),
        sa.Column('portal_login_password', sa.String(length=128), nullable=True),
        sa.Column('enable_portal_login', sa.Boolean(), nullable=False, default=False),
        sa.Column('change_user_info', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=128), nullable=True),
        sa.Column('updated_by', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_username_active', 'users', ['username', 'is_active'])
    op.create_index('idx_users_email_active', 'users', ['email', 'is_active'])
    op.create_index('idx_users_status', 'users', ['status'])

    # Create legacy userinfo table for compatibility
    op.create_table('userinfo',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('firstname', sa.String(length=200), nullable=True),
        sa.Column('lastname', sa.String(length=200), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('department', sa.String(length=200), nullable=True),
        sa.Column('company', sa.String(length=200), nullable=True),
        sa.Column('workphone', sa.String(length=200), nullable=True),
        sa.Column('homephone', sa.String(length=200), nullable=True),
        sa.Column('mobilephone', sa.String(length=200), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=200), nullable=True),
        sa.Column('state', sa.String(length=200), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('zip', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('changeuserinfo', sa.Integer(), default=0),
        sa.Column('portalloginpassword', sa.String(length=128), nullable=True),
        sa.Column('enableportallogin', sa.Integer(), default=0),
        sa.Column('creationdate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('creationby', sa.String(length=128), nullable=True),
        sa.Column('updatedate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updateby', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_userinfo_username', 'userinfo', ['username'])

    # Create radcheck table
    op.create_table('radcheck',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('attribute', sa.String(length=64), nullable=False),
        sa.Column('op', sa.String(length=2), nullable=False, default='=='),
        sa.Column('value', sa.String(length=253), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_radcheck_username', 'radcheck', ['username'])
    op.create_index('idx_radcheck_username_attribute', 'radcheck', ['username', 'attribute'])

    # Create radreply table
    op.create_table('radreply',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('attribute', sa.String(length=64), nullable=False),
        sa.Column('op', sa.String(length=2), nullable=False, default='='),
        sa.Column('value', sa.String(length=253), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_radreply_username', 'radreply', ['username'])
    op.create_index('idx_radreply_username_attribute', 'radreply', ['username', 'attribute'])

    # Create radacct table (accounting)
    op.create_table('radacct',
        sa.Column('radacctid', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('acctsessionid', sa.String(length=64), nullable=False),
        sa.Column('acctuniqueid', sa.String(length=32), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('realm', sa.String(length=64), nullable=True),
        sa.Column('nasipaddress', postgresql.INET(), nullable=False),
        sa.Column('nasportid', sa.String(length=32), nullable=True),
        sa.Column('nasporttype', sa.String(length=32), nullable=True),
        sa.Column('acctstarttime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acctupdatetime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acctstoptime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acctinterval', sa.Integer(), nullable=True),
        sa.Column('acctsessiontime', sa.Integer(), nullable=True),
        sa.Column('acctauthentic', sa.String(length=32), nullable=True),
        sa.Column('connectinfo_start', sa.String(length=128), nullable=True),
        sa.Column('connectinfo_stop', sa.String(length=128), nullable=True),
        sa.Column('acctinputoctets', sa.BigInteger(), nullable=True),
        sa.Column('acctoutputoctets', sa.BigInteger(), nullable=True),
        sa.Column('calledstationid', sa.String(length=50), nullable=True),
        sa.Column('callingstationid', sa.String(length=50), nullable=True),
        sa.Column('acctterminatecause', sa.String(length=32), nullable=True),
        sa.Column('servicetype', sa.String(length=32), nullable=True),
        sa.Column('framedprotocol', sa.String(length=32), nullable=True),
        sa.Column('framedipaddress', postgresql.INET(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('radacctid')
    )
    op.create_index('idx_radacct_username', 'radacct', ['username'])
    op.create_index('idx_radacct_acctstarttime', 'radacct', ['acctstarttime'])
    op.create_index('idx_radacct_acctstoptime', 'radacct', ['acctstoptime'])
    op.create_index('idx_radacct_nasipaddress', 'radacct', ['nasipaddress'])
    op.create_index('idx_radacct_acctsessionid', 'radacct', ['acctsessionid'])

    # Create nas table
    op.create_table('nas',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('nasname', sa.String(length=128), nullable=False),
        sa.Column('shortname', sa.String(length=32), nullable=True),
        sa.Column('type', sa.String(length=30), nullable=True, default='other'),
        sa.Column('ports', sa.Integer(), nullable=True),
        sa.Column('secret', sa.String(length=60), nullable=False),
        sa.Column('server', sa.String(length=64), nullable=True),
        sa.Column('community', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nasname')
    )
    op.create_index('idx_nas_nasname', 'nas', ['nasname'])

    # Create groups table
    op.create_table('radgroups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('groupname', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, default=1),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=128), nullable=True),
        sa.Column('updated_by', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('groupname')
    )
    op.create_index('idx_radgroups_groupname', 'radgroups', ['groupname'])

    # Create radusergroup table
    op.create_table('radusergroup',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('groupname', sa.String(length=64), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=128), nullable=True),
        sa.Column('updated_by', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username', 'groupname', name='uq_user_group')
    )
    op.create_index('idx_user_group_username', 'radusergroup', ['username'])
    op.create_index('idx_user_group_groupname', 'radusergroup', ['groupname'])

    # Create billing info table
    op.create_table('dalouserbillinfo',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('planname', sa.String(length=128), nullable=True),
        sa.Column('contactperson', sa.String(length=200), nullable=True),
        sa.Column('company', sa.String(length=200), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=200), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=200), nullable=True),
        sa.Column('state', sa.String(length=200), nullable=True),
        sa.Column('country', sa.String(length=200), nullable=True),
        sa.Column('zip', sa.String(length=200), nullable=True),
        sa.Column('paymentmethod', sa.String(length=200), nullable=True),
        sa.Column('cash', sa.String(length=200), nullable=True),
        sa.Column('creditcardname', sa.String(length=200), nullable=True),
        sa.Column('creditcardnumber', sa.String(length=200), nullable=True),
        sa.Column('creditcardverification', sa.String(length=200), nullable=True),
        sa.Column('creditcardtype', sa.String(length=200), nullable=True),
        sa.Column('creditcardexp', sa.String(length=200), nullable=True),
        sa.Column('lead', sa.String(length=200), nullable=True),
        sa.Column('coupon', sa.String(length=200), nullable=True),
        sa.Column('ordertaker', sa.String(length=200), nullable=True),
        sa.Column('billstatus', sa.String(length=200), nullable=True),
        sa.Column('lastbill', sa.Date(), nullable=True),
        sa.Column('nextbill', sa.Date(), nullable=True),
        sa.Column('nextinvoicedue', sa.Date(), nullable=True),
        sa.Column('billdue', sa.Date(), nullable=True),
        sa.Column('postalinvoice', sa.String(length=200), nullable=True),
        sa.Column('faxinvoice', sa.String(length=200), nullable=True),
        sa.Column('emailinvoice', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('changeuserbillinfo', sa.Integer(), default=0),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=128), nullable=True),
        sa.Column('updated_by', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_userbillinfo_username', 'dalouserbillinfo', ['username'])
    op.create_index('idx_userbillinfo_planname', 'dalouserbillinfo', ['planname'])

    # Create batch_history table
    op.create_table('batch_history',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('batch_name', sa.String(length=128), nullable=False),
        sa.Column('batch_description', sa.Text(), nullable=True),
        sa.Column('hotspot_id', sa.Integer(), nullable=True),
        sa.Column('creationdate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('creationby', sa.String(length=128), nullable=True),
        sa.Column('updatedate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updateby', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop all daloRADIUS tables"""
    op.drop_table('batch_history')
    op.drop_table('dalouserbillinfo')
    op.drop_table('radusergroup')
    op.drop_table('radgroups')
    op.drop_table('nas')
    op.drop_table('radacct')
    op.drop_table('radreply')
    op.drop_table('radcheck')
    op.drop_table('userinfo')
    op.drop_table('users')
    op.drop_table('operators')
"""Create access control tables

Revision ID: 005_access_control
Revises: 004_billing_system
Create Date: 2025-09-27 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_access_control'
down_revision = '004_billing_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create access control tables"""
    
    # Create operators_acl table
    op.create_table('operators_acl',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('operator_id', sa.Integer(), nullable=False),
        sa.Column('file', sa.String(length=128), nullable=False),
        sa.Column('access', sa.SmallInteger(), nullable=False, default=0),
        sa.ForeignKeyConstraint(['operator_id'], ['operators.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_operators_acl_operator_id', 'operators_acl', ['operator_id'])
    op.create_index('idx_operators_acl_file', 'operators_acl', ['file'])
    op.create_index('idx_operators_acl_operator_file', 'operators_acl', ['operator_id', 'file'], unique=True)

    # Create operators_acl_files table
    op.create_table('operators_acl_files',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('file', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file')
    )
    op.create_index('idx_operators_acl_files_category', 'operators_acl_files', ['category'])
    op.create_index('idx_operators_acl_files_active', 'operators_acl_files', ['is_active'])

    # Create dictionary table
    op.create_table('dictionary',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('Type', sa.String(length=30), nullable=True),
        sa.Column('Attribute', sa.String(length=64), nullable=True),
        sa.Column('Value', sa.String(length=64), nullable=True),
        sa.Column('Format', sa.String(length=20), nullable=True),
        sa.Column('Vendor', sa.String(length=32), nullable=True),
        sa.Column('RecommendedOP', sa.String(length=32), nullable=True),
        sa.Column('RecommendedTable', sa.String(length=32), nullable=True),
        sa.Column('RecommendedHelper', sa.String(length=32), nullable=True),
        sa.Column('RecommendedTooltip', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dictionary_attribute', 'dictionary', ['Attribute'])
    op.create_index('idx_dictionary_vendor', 'dictionary', ['Vendor'])
    op.create_index('idx_dictionary_type', 'dictionary', ['Type'])

    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('type', sa.Enum('login', 'support', 'dashboard', name='message_type'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=32), nullable=True),
        sa.Column('modified_on', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_by', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_type', 'messages', ['type'])
    op.create_index('idx_messages_created_on', 'messages', ['created_on'])

    # Insert default ACL files configuration
    op.execute("""
        INSERT INTO operators_acl_files (file, category, description, is_active) VALUES
        ('acct_custom_query', 'Accounting', 'Custom accounting queries', true),
        ('acct_active', 'Accounting', 'Active sessions view', true),
        ('acct_all', 'Accounting', 'All accounting records', true),
        ('acct_ipaddress', 'Accounting', 'Search by IP address', true),
        ('acct_username', 'Accounting', 'Search by username', true),
        ('acct_date', 'Accounting', 'Search by date range', true),
        ('acct_nasipaddress', 'Accounting', 'Search by NAS IP', true),
        ('acct_hotspot_accounting', 'Accounting', 'Hotspot accounting', true),
        ('acct_hotspot_compare', 'Accounting', 'Hotspot comparison', true),
        ('acct_maintenance_cleanup', 'Maintenance', 'Cleanup accounting', true),
        ('acct_maintenance_delete', 'Maintenance', 'Delete accounting', true),
        ('acct_plans_usage', 'Plans', 'Plans usage reports', true),
        ('bill_history_query', 'Billing', 'Billing history queries', true),
        ('bill_merchant_transactions', 'Billing', 'Merchant transactions', true),
        ('bill_plans_list', 'Billing', 'List billing plans', true),
        ('bill_plans_del', 'Billing', 'Delete billing plans', true),
        ('bill_plans_edit', 'Billing', 'Edit billing plans', true),
        ('bill_plans_new', 'Billing', 'Create billing plans', true),
        ('bill_rates_list', 'Billing', 'List billing rates', true),
        ('bill_rates_new', 'Billing', 'Create billing rates', true),
        ('bill_rates_edit', 'Billing', 'Edit billing rates', true),
        ('bill_rates_del', 'Billing', 'Delete billing rates', true),
        ('mng_users_list', 'Users', 'List users', true),
        ('mng_users_new', 'Users', 'Create users', true),
        ('mng_users_edit', 'Users', 'Edit users', true),
        ('mng_users_del', 'Users', 'Delete users', true),
        ('config_backup_managebackups', 'Config', 'Manage backups', true),
        ('config_backup_createbackups', 'Config', 'Create backups', true),
        ('config_user', 'Config', 'User configuration', true)
    """)

    # Insert default messages
    op.execute("""
        INSERT INTO messages (type, content, created_by) VALUES
        ('login', '<p>Dear User,<br>Welcome to the Users Portal. We are glad you joined us!</p><p>By logging in with your account username and password, you will be able to access a wide range of features. For example, you can easily edit your contact settings, update your personal information, and view some history data through visual graphs.</p><p>We take your privacy and security seriously, so please rest assured that all your data is stored securely in our database and is accessible only to you and our authorized staff.</p><p>If you need any assistance or have any questions, please do not hesitate to contact our support team. We are always happy to help!</p><p>Regards,<br/>The daloRADIUS Staff.</p>', 'administrator'),
        ('support', '<p>Dear User,<br>We can provide support in different ways: you can email us at <strong>support@daloradius.local</strong> or you can open a new ticket through our help desk: <strong>https://helpdesk.daloradius.local</strong>.</p><p>Thank you for choosing daloRADIUS.</p><p>Best regards,<br>The daloRADIUS Support Team</p>', 'administrator'),
        ('dashboard', '<p>Dear User,<br>We can provide support in different ways: you can email us at <strong>support@daloradius.local</strong> or you can open a new ticket through our help desk: <strong>https://helpdesk.daloradius.local</strong>.</p><p>Thank you for choosing daloRADIUS.</p><p>Best regards,<br>The daloRADIUS Support Team</p>', 'administrator')
    """)


def downgrade() -> None:
    """Drop access control tables"""
    
    op.drop_table('messages')
    op.drop_table('dictionary')
    op.drop_table('operators_acl_files')
    op.drop_table('operators_acl')
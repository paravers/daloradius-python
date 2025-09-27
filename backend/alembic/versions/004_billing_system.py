"""Create billing system tables

Revision ID: 004_billing_system
Revises: 003_radius_groups
Create Date: 2025-09-27 12:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_billing_system'
down_revision = '003_radius_groups'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create billing system tables"""
    
    # Create billing_plans table
    op.create_table('billing_plans',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('planName', sa.String(length=128), nullable=True),
        sa.Column('planId', sa.String(length=128), nullable=True),
        sa.Column('planType', sa.String(length=128), nullable=True),
        sa.Column('planTimeBank', sa.String(length=128), nullable=True),
        sa.Column('planTimeType', sa.String(length=128), nullable=True),
        sa.Column('planTimeRefillCost', sa.String(length=128), nullable=True),
        sa.Column('planBandwidthUp', sa.String(length=128), nullable=True),
        sa.Column('planBandwidthDown', sa.String(length=128), nullable=True),
        sa.Column('planTrafficTotal', sa.String(length=128), nullable=True),
        sa.Column('planTrafficUp', sa.String(length=128), nullable=True),
        sa.Column('planTrafficDown', sa.String(length=128), nullable=True),
        sa.Column('planTrafficRefillCost', sa.String(length=128), nullable=True),
        sa.Column('planRecurring', sa.String(length=128), nullable=True),
        sa.Column('planRecurringPeriod', sa.String(length=128), nullable=True),
        sa.Column('planRecurringBillingSchedule', sa.String(length=128), nullable=False, default='Fixed'),
        sa.Column('planCost', sa.String(length=128), nullable=True),
        sa.Column('planSetupCost', sa.String(length=128), nullable=True),
        sa.Column('planTax', sa.String(length=128), nullable=True),
        sa.Column('planCurrency', sa.String(length=128), nullable=True),
        sa.Column('planGroup', sa.String(length=128), nullable=True),
        sa.Column('planActive', sa.String(length=32), nullable=False, default='yes'),
        sa.Column('creationdate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('creationby', sa.String(length=128), nullable=True),
        sa.Column('updatedate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updateby', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_billing_plans_planName', 'billing_plans', ['planName'])
    op.create_index('idx_billing_plans_planActive', 'billing_plans', ['planActive'])

    # Create billing_history table
    op.create_table('billing_history',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('username', sa.String(length=128), nullable=True),
        sa.Column('planId', sa.Integer(), nullable=True),
        sa.Column('billAmount', sa.String(length=200), nullable=True),
        sa.Column('billAction', sa.String(length=128), nullable=False, default='Unavailable'),
        sa.Column('billPerformer', sa.String(length=200), nullable=True),
        sa.Column('billReason', sa.String(length=200), nullable=True),
        sa.Column('paymentmethod', sa.String(length=200), nullable=True),
        sa.Column('cash', sa.String(length=200), nullable=True),
        sa.Column('creditcardname', sa.String(length=200), nullable=True),
        sa.Column('creditcardnumber', sa.String(length=200), nullable=True),
        sa.Column('creditcardverification', sa.String(length=200), nullable=True),
        sa.Column('creditcardtype', sa.String(length=200), nullable=True),
        sa.Column('creditcardexp', sa.String(length=200), nullable=True),
        sa.Column('coupon', sa.String(length=200), nullable=True),
        sa.Column('discount', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.String(length=200), nullable=True),
        sa.Column('creationdate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('creationby', sa.String(length=128), nullable=True),
        sa.Column('updatedate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updateby', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_billing_history_username', 'billing_history', ['username'])
    op.create_index('idx_billing_history_planId', 'billing_history', ['planId'])

    # Create billing_merchant table
    op.create_table('billing_merchant',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('username', sa.String(length=128), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('mac', sa.String(length=200), nullable=False),
        sa.Column('pin', sa.String(length=200), nullable=False),
        sa.Column('txnId', sa.String(length=200), nullable=False),
        sa.Column('planName', sa.String(length=128), nullable=False),
        sa.Column('planId', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.String(length=200), nullable=False),
        sa.Column('business_email', sa.String(length=200), nullable=False),
        sa.Column('business_id', sa.String(length=200), nullable=False),
        sa.Column('txn_type', sa.String(length=200), nullable=False),
        sa.Column('txn_id', sa.String(length=200), nullable=False),
        sa.Column('payment_type', sa.String(length=200), nullable=False),
        sa.Column('payment_tax', sa.String(length=200), nullable=False),
        sa.Column('payment_cost', sa.String(length=200), nullable=False),
        sa.Column('payment_fee', sa.String(length=200), nullable=False),
        sa.Column('payment_total', sa.String(length=200), nullable=False),
        sa.Column('payment_currency', sa.String(length=200), nullable=False),
        sa.Column('first_name', sa.String(length=200), nullable=False),
        sa.Column('last_name', sa.String(length=200), nullable=False),
        sa.Column('payer_email', sa.String(length=200), nullable=False),
        sa.Column('payer_address_name', sa.String(length=200), nullable=False),
        sa.Column('payer_address_street', sa.String(length=200), nullable=False),
        sa.Column('payer_address_country', sa.String(length=200), nullable=False),
        sa.Column('payer_address_country_code', sa.String(length=200), nullable=False),
        sa.Column('payer_address_city', sa.String(length=200), nullable=False),
        sa.Column('payer_address_state', sa.String(length=200), nullable=False),
        sa.Column('payer_address_zip', sa.String(length=200), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('payment_status', sa.String(length=200), nullable=False),
        sa.Column('pending_reason', sa.String(length=200), nullable=False),
        sa.Column('reason_code', sa.String(length=200), nullable=False),
        sa.Column('receipt_ID', sa.String(length=200), nullable=False),
        sa.Column('payment_address_status', sa.String(length=200), nullable=False),
        sa.Column('vendor_type', sa.String(length=200), nullable=False),
        sa.Column('payer_status', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_billing_merchant_username', 'billing_merchant', ['username'])
    op.create_index('idx_billing_merchant_txnId', 'billing_merchant', ['txnId'])

    # Create billing_rates table
    op.create_table('billing_rates',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('rateName', sa.String(length=128), nullable=False),
        sa.Column('rateType', sa.String(length=128), nullable=False),
        sa.Column('rateCost', sa.Integer(), nullable=False, default=0),
        sa.Column('creationdate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('creationby', sa.String(length=128), nullable=True),
        sa.Column('updatedate', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updateby', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_billing_rates_rateName', 'billing_rates', ['rateName'])

    # Create billing_plans_profiles table
    op.create_table('billing_plans_profiles',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('plan_name', sa.String(length=128), nullable=False),
        sa.Column('profile_name', sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop billing system tables"""
    
    op.drop_table('billing_plans_profiles')
    op.drop_table('billing_rates')
    op.drop_table('billing_merchant')
    op.drop_table('billing_history')
    op.drop_table('billing_plans')
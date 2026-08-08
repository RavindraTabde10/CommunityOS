"""add asset and facility management tables

Revision ID: fe8c7d9b4a21
Revises: 2e03aadabdf3
Create Date: 2026-07-25 06:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe8c7d9b4a21'
down_revision = '2e03aadabdf3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create assets table
    op.create_table('assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('asset_type', sa.Enum('GYM', 'POOL', 'CLUBHOUSE', 'PARTY_HALL', 'SPORTS_COURT', 'MEETING_ROOM', 'PARKING', 'OTHER', name='assettype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('is_bookable', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('hourly_rate', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('advance_booking_days', sa.Integer(), nullable=True),
        sa.Column('min_booking_duration', sa.Integer(), nullable=True),
        sa.Column('max_booking_duration', sa.Integer(), nullable=True),
        sa.Column('operating_hours_start', sa.Time(), nullable=True),
        sa.Column('operating_hours_end', sa.Time(), nullable=True),
        sa.Column('qr_code_data', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('qr_code_data')
    )
    op.create_index(op.f('ix_assets_is_active'), 'assets', ['is_active'], unique=False)
    
    # Create asset_bookings table
    op.create_table('asset_bookings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('booking_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.Text(), nullable=True),
        sa.Column('number_of_guests', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW', name='bookingstatus'), nullable=False),
        sa.Column('payment_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('payment_status', sa.Enum('PENDING', 'PAID', 'REFUNDED', name='paymentstatus'), nullable=False),
        sa.Column('checked_in_at', sa.DateTime(), nullable=True),
        sa.Column('checked_out_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_bookings_asset_id'), 'asset_bookings', ['asset_id'], unique=False)
    op.create_index(op.f('ix_asset_bookings_booking_date'), 'asset_bookings', ['booking_date'], unique=False)
    op.create_index(op.f('ix_asset_bookings_status'), 'asset_bookings', ['status'], unique=False)
    op.create_index(op.f('ix_asset_bookings_user_id'), 'asset_bookings', ['user_id'], unique=False)
    
    # Create asset_maintenance table
    op.create_table('asset_maintenance',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('maintenance_type', sa.Enum('ROUTINE', 'REPAIR', 'INSPECTION', 'CLEANING', name='maintenancetype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('performed_by', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='maintenancestatus'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('asset_maintenance')
    
    op.drop_index(op.f('ix_asset_bookings_user_id'), table_name='asset_bookings')
    op.drop_index(op.f('ix_asset_bookings_status'), table_name='asset_bookings')
    op.drop_index(op.f('ix_asset_bookings_booking_date'), table_name='asset_bookings')
    op.drop_index(op.f('ix_asset_bookings_asset_id'), table_name='asset_bookings')
    op.drop_table('asset_bookings')
    
    op.drop_index(op.f('ix_assets_is_active'), table_name='assets')
    op.drop_table('assets')

"""add_vehicle_fields_to_water_tanker_orders

Revision ID: 265ddde27a5b
Revises: 214e75e25c83
Create Date: 2026-08-07 12:47:59.859070

"""
from alembic import op
import sqlalchemy as sa

revision = '265ddde27a5b'
down_revision = '214e75e25c83'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('water_tanker_orders', sa.Column('vehicle_number', sa.String(), nullable=True))
    op.add_column('water_tanker_orders', sa.Column('driver_name',    sa.String(), nullable=True))
    op.add_column('water_tanker_orders', sa.Column('driver_phone',   sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('water_tanker_orders', 'driver_phone')
    op.drop_column('water_tanker_orders', 'driver_name')
    op.drop_column('water_tanker_orders', 'vehicle_number')

"""add_departed_time_to_water_tanker_orders

Revision ID: f10f57cd177a
Revises: 265ddde27a5b
Create Date: 2026-08-07 12:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f10f57cd177a'
down_revision = '265ddde27a5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('water_tanker_orders', sa.Column('departed_time', sa.Time(), nullable=True))


def downgrade() -> None:
    op.drop_column('water_tanker_orders', 'departed_time')

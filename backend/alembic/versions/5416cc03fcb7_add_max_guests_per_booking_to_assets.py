"""add_max_guests_per_booking_to_assets

Revision ID: 5416cc03fcb7
Revises: h5i6j7k8l9m0
Create Date: 2026-08-07 11:10:32.537056

"""
from alembic import op
import sqlalchemy as sa


revision = '5416cc03fcb7'
down_revision = 'h5i6j7k8l9m0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('assets', sa.Column('max_guests_per_booking', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('assets', 'max_guests_per_booking')

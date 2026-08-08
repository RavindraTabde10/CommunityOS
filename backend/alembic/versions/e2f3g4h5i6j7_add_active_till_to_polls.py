"""add_active_till_to_polls

Revision ID: e2f3g4h5i6j7
Revises: d1f2e3a4b5c6
Create Date: 2026-08-04 08:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "e2f3g4h5i6j7"
down_revision = "d1f2e3a4b5c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("polls", sa.Column("active_till", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("polls", "active_till")

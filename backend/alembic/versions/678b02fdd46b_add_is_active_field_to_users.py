"""add_is_active_field_to_users

Revision ID: 678b02fdd46b
Revises: c8b572f8dbff
Create Date: 2026-07-23 17:20:28.363311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '678b02fdd46b'
down_revision = 'c8b572f8dbff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_active column with default value True
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    # Remove is_active column
    op.drop_column('users', 'is_active')

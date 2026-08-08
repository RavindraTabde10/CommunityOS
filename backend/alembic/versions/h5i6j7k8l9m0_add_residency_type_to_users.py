"""add_residency_type_to_users

Revision ID: h5i6j7k8l9m0
Revises: d2e3f4g5h6i7
Create Date: 2026-08-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'h5i6j7k8l9m0'
down_revision = 'd2e3f4g5h6i7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'residency_type',
            sa.Enum('owner', 'tenant', name='residencytype'),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column('users', 'residency_type')
    op.execute("DROP TYPE IF EXISTS residencytype")

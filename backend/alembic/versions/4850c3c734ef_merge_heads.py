"""merge_heads

Revision ID: 4850c3c734ef
Revises: 09cbc9be3975, 4a1b2c3d4e5f
Create Date: 2026-07-23 16:55:31.705010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4850c3c734ef'
down_revision = ('09cbc9be3975', '4a1b2c3d4e5f')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

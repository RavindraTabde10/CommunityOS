"""fix_committee_user_id_type

Fix user_id column in committee_members from Integer to String (UUID)
to match users.id which is a UUID string primary key.

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2026-08-07 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b1c2d3e4f5g6'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('committee_members', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.Integer(),
               type_=sa.String(36),
               existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('committee_members', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.String(36),
               type_=sa.Integer(),
               existing_nullable=False)

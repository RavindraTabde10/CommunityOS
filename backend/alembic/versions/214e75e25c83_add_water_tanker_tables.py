"""add_water_tanker_tables

Revision ID: 214e75e25c83
Revises: 5416cc03fcb7
Create Date: 2026-08-07 12:41:49.228593

"""
from alembic import op
import sqlalchemy as sa

revision = '214e75e25c83'
down_revision = '5416cc03fcb7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('water_tanker_suppliers',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('contact_name', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('capacity_kl', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('rate_per_kl', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('water_tanker_orders',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('supplier_id', sa.String(), nullable=True),
    sa.Column('scheduled_date', sa.Date(), nullable=False),
    sa.Column('scheduled_time', sa.Time(), nullable=True),
    sa.Column('quantity_kl', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.Column('actual_quantity_kl', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='scheduled'),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['supplier_id'], ['water_tanker_suppliers.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('water_tanker_orders')
    op.drop_table('water_tanker_suppliers')

"""add_security_guidelines_table

Revision ID: d2e3f4g5h6i7
Revises: b5b1dc085bd0
Create Date: 2026-08-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd2e3f4g5h6i7'
down_revision = 'b5b1dc085bd0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'security_guidelines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('text', sa.String(500), nullable=False),
        sa.Column('text_hi', sa.String(500), nullable=True),
        sa.Column('icon_type', sa.String(20), nullable=False, server_default='check'),
        sa.Column('severity', sa.String(20), nullable=False, server_default='#e8f5e9'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # Seed default guidelines
    op.bulk_insert(
        sa.table(
            'security_guidelines',
            sa.column('text', sa.String),
            sa.column('text_hi', sa.String),
            sa.column('icon_type', sa.String),
            sa.column('severity', sa.String),
            sa.column('sort_order', sa.Integer),
            sa.column('is_active', sa.Boolean),
        ),
        [
            {'text': 'No entry without resident approval', 'text_hi': 'बिना अनुमति के कोई प्रवेश नहीं', 'icon_type': 'block', 'severity': '#ffebee', 'sort_order': 0, 'is_active': True},
            {'text': 'Log every visitor — no exceptions', 'text_hi': 'हर विज़िटर की एंट्री जरूरी है', 'icon_type': 'check', 'severity': '#e8f5e9', 'sort_order': 1, 'is_active': True},
            {'text': 'Verify visitor ID before allowing entry', 'text_hi': 'प्रवेश से पहले पहचान पत्र जांचें', 'icon_type': 'badge', 'severity': '#e3f2fd', 'sort_order': 2, 'is_active': True},
            {'text': 'Note vehicle number for all vehicles', 'text_hi': 'सभी वाहनों का नंबर दर्ज करें', 'icon_type': 'car', 'severity': '#fff3e0', 'sort_order': 3, 'is_active': True},
            {'text': 'Report suspicious activity immediately', 'text_hi': 'संदिग्ध गतिविधि तुरंत सूचित करें', 'icon_type': 'warning', 'severity': '#fffde7', 'sort_order': 4, 'is_active': True},
        ],
    )


def downgrade() -> None:
    op.drop_table('security_guidelines')

"""Add issue_number field for RGTS ID format

Revision ID: 4a1b2c3d4e5f
Revises: 3f2d80960de8
Create Date: 2026-07-23 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a1b2c3d4e5f'
down_revision = '3f2d80960de8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add issue_number column using batch mode for SQLite
    with op.batch_alter_table('issues', schema=None) as batch_op:
        batch_op.add_column(sa.Column('issue_number', sa.String(), nullable=True))
    
    # Migrate existing issues to have issue_number
    # This SQL will update existing records with sequential numbers
    op.execute("""
        UPDATE issues
        SET issue_number = printf('%06d', CAST(SUBSTR(id, 1, INSTR(id, '-') - 1) AS INTEGER))
        WHERE issue_number IS NULL AND id LIKE '%-%'
    """)
    
    # For UUID-based IDs, assign sequential numbers
    op.execute("""
        UPDATE issues
        SET issue_number = printf('%06d', ROWID)
        WHERE issue_number IS NULL
    """)
    
    # Update existing IDs to RGTS format if they're not already
    op.execute("""
        UPDATE issues
        SET id = 'RGTS-' || issue_number
        WHERE id NOT LIKE 'RGTS-%'
    """)
    
    # Now make issue_number UNIQUE using batch mode
    with op.batch_alter_table('issues', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_issues_issue_number', ['issue_number'])


def downgrade() -> None:
    # Remove unique constraint and column using batch mode
    with op.batch_alter_table('issues', schema=None) as batch_op:
        batch_op.drop_constraint('uq_issues_issue_number', type_='unique')
        batch_op.drop_column('issue_number')

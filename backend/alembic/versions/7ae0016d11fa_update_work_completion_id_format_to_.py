"""update work completion id format to wkcmp-xxxxxx

Revision ID: 7ae0016d11fa
Revises: 0c5b8423bf9d
Create Date: 2026-07-25 06:56:56.338045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ae0016d11fa'
down_revision = '0c5b8423bf9d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Update work_completions ID format from UUID to WKCMP-XXXXXX
    """
    # Create a connection
    conn = op.get_bind()
    
    # Step 1: Get existing work completions with their old UUIDs
    result = conn.execute(sa.text("SELECT id FROM work_completions ORDER BY completed_at"))
    old_completions = result.fetchall()
    
    # Step 2: Create mapping of old UUID to new WKCMP-XXXXXX format
    id_mapping = {}
    for idx, row in enumerate(old_completions, start=1):
        old_id = row[0]
        new_id = f"WKCMP-{idx:06d}"
        id_mapping[old_id] = new_id
    
    # Step 3: Update work_completions IDs
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE work_completions SET id = :new_id WHERE id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )


def downgrade() -> None:
    """
    Downgrade is not supported as it would require regenerating UUIDs
    which cannot be done deterministically
    """
    pass

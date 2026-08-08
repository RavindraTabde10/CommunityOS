"""update contractor id format to contcr-xxxxxx

Revision ID: 0c5b8423bf9d
Revises: fe8c7d9b4a21
Create Date: 2026-07-25 06:42:14.814955

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = '0c5b8423bf9d'
down_revision = 'fe8c7d9b4a21'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Update contractor_profiles ID format from UUID to CONTCR-XXXXXX
    Also updates related foreign keys in contractor_ratings and work_completions
    """
    # Create a connection
    conn = op.get_bind()
    
    # Step 1: Get existing contractors with their old UUIDs
    result = conn.execute(sa.text("SELECT id FROM contractor_profiles ORDER BY created_at"))
    old_contractors = result.fetchall()
    
    # Step 2: Create mapping of old UUID to new CONTCR-XXXXXX format
    id_mapping = {}
    for idx, row in enumerate(old_contractors, start=1):
        old_id = row[0]
        new_id = f"CONTCR-{idx:06d}"
        id_mapping[old_id] = new_id
    
    # Step 3: Update contractor_profiles IDs
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE contractor_profiles SET id = :new_id WHERE id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Step 4: Update foreign keys in contractor_ratings
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE contractor_ratings SET contractor_id = :new_id WHERE contractor_id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )
    
    # Step 5: Update foreign keys in work_completions
    for old_id, new_id in id_mapping.items():
        conn.execute(
            sa.text("UPDATE work_completions SET contractor_id = :new_id WHERE contractor_id = :old_id"),
            {"new_id": new_id, "old_id": old_id}
        )


def downgrade() -> None:
    """
    Downgrade is not supported as it would require regenerating UUIDs
    which cannot be done deterministically
    """
    pass

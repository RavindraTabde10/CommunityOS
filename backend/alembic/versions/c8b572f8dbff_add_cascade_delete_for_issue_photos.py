"""add_cascade_delete_for_issue_photos

Revision ID: c8b572f8dbff
Revises: 4850c3c734ef
Create Date: 2026-07-23 16:55:40.772346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8b572f8dbff'
down_revision = '4850c3c734ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # For SQLite, we need to recreate the table with ON DELETE CASCADE
    # First, check if we're using SQLite
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        # SQLite doesn't support ALTER CONSTRAINT, so we recreate the table
        op.execute('''
            CREATE TABLE issue_photos_new (
                id VARCHAR NOT NULL,
                issue_id VARCHAR,
                photo_url VARCHAR NOT NULL,
                uploaded_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                PRIMARY KEY (id),
                FOREIGN KEY(issue_id) REFERENCES issues (id) ON DELETE CASCADE
            )
        ''')
        
        # Copy data from old table
        op.execute('INSERT INTO issue_photos_new SELECT * FROM issue_photos')
        
        # Drop old table and rename new table
        op.execute('DROP TABLE issue_photos')
        op.execute('ALTER TABLE issue_photos_new RENAME TO issue_photos')
    else:
        # For PostgreSQL, we can drop and recreate the constraint
        op.drop_constraint('issue_photos_issue_id_fkey', 'issue_photos', type_='foreignkey')
        op.create_foreign_key(
            'issue_photos_issue_id_fkey',
            'issue_photos', 'issues',
            ['issue_id'], ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    # Revert the cascade delete
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        # SQLite: recreate table without CASCADE
        op.execute('''
            CREATE TABLE issue_photos_old (
                id VARCHAR NOT NULL,
                issue_id VARCHAR,
                photo_url VARCHAR NOT NULL,
                uploaded_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                PRIMARY KEY (id),
                FOREIGN KEY(issue_id) REFERENCES issues (id)
            )
        ''')
        op.execute('INSERT INTO issue_photos_old SELECT * FROM issue_photos')
        op.execute('DROP TABLE issue_photos')
        op.execute('ALTER TABLE issue_photos_old RENAME TO issue_photos')
    else:
        # PostgreSQL
        op.drop_constraint('issue_photos_issue_id_fkey', 'issue_photos', type_='foreignkey')
        op.create_foreign_key(
            'issue_photos_issue_id_fkey',
            'issue_photos', 'issues',
            ['issue_id'], ['id']
        )

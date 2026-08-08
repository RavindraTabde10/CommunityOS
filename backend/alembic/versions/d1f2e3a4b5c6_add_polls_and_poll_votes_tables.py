"""add_polls_and_poll_votes_tables

Revision ID: d1f2e3a4b5c6
Revises: 9d0e1f2g3h4i
Create Date: 2026-08-03 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d1f2e3a4b5c6"
down_revision = "9d0e1f2g3h4i"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "polls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_polls_id"), "polls", ["id"], unique=False)
    op.create_index(op.f("ix_polls_is_active"), "polls", ["is_active"], unique=False)

    op.create_table(
        "poll_votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("poll_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("option_index", sa.Integer(), nullable=False),
        sa.Column("voted_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["poll_id"], ["polls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("poll_id", "user_id", name="uq_poll_vote_user"),
    )
    op.create_index(op.f("ix_poll_votes_id"), "poll_votes", ["id"], unique=False)
    op.create_index(op.f("ix_poll_votes_poll_id"), "poll_votes", ["poll_id"], unique=False)
    op.create_index(op.f("ix_poll_votes_user_id"), "poll_votes", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_poll_votes_user_id"), table_name="poll_votes")
    op.drop_index(op.f("ix_poll_votes_poll_id"), table_name="poll_votes")
    op.drop_index(op.f("ix_poll_votes_id"), table_name="poll_votes")
    op.drop_table("poll_votes")

    op.drop_index(op.f("ix_polls_is_active"), table_name="polls")
    op.drop_index(op.f("ix_polls_id"), table_name="polls")
    op.drop_table("polls")

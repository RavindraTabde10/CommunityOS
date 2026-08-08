"""Phase 4 – performance indexes and audit_log table

Revision ID: a1b2c3d4e5f6
Revises: f10f57cd177a
Create Date: 2026-08-07 00:00:00.000000

Adds:
  - audit_logs table
  - Composite / single-column indexes on hot query paths (issues, users, comments)
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "f10f57cd177a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # audit_logs table
    # ------------------------------------------------------------------
    op.create_table(
        "api_audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("user_email", sa.String(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("http_method", sa.String(length=10), nullable=True),
        sa.Column("endpoint", sa.String(length=255), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_audit_logs_user_id", "api_audit_logs", ["user_id"])
    op.create_index("ix_api_audit_logs_action", "api_audit_logs", ["action"])
    op.create_index("ix_api_audit_logs_created_at", "api_audit_logs", ["created_at"])

    # ------------------------------------------------------------------
    # Performance indexes on issues table
    # ------------------------------------------------------------------
    op.create_index("ix_issues_status", "issues", ["status"])
    op.create_index("ix_issues_category", "issues", ["category"])
    op.create_index("ix_issues_priority", "issues", ["priority"])
    op.create_index("ix_issues_reported_by", "issues", ["reported_by"])
    op.create_index("ix_issues_assigned_to", "issues", ["assigned_to"])
    op.create_index("ix_issues_created_at", "issues", ["created_at"])
    # Compound index for the common "my open issues" query
    op.create_index(
        "ix_issues_reported_by_status", "issues", ["reported_by", "status"]
    )

    # ------------------------------------------------------------------
    # Performance indexes on users table
    # ------------------------------------------------------------------
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    # ------------------------------------------------------------------
    # Performance indexes on comments table
    # ------------------------------------------------------------------
    op.create_index("ix_comments_issue_id", "comments", ["issue_id"])
    op.create_index("ix_comments_user_id", "comments", ["user_id"])

    # ------------------------------------------------------------------
    # Performance indexes on issue_photos table
    # ------------------------------------------------------------------
    op.create_index("ix_issue_photos_issue_id", "issue_photos", ["issue_id"])


def downgrade() -> None:
    op.drop_index("ix_issue_photos_issue_id", table_name="issue_photos")

    op.drop_index("ix_comments_user_id", table_name="comments")
    op.drop_index("ix_comments_issue_id", table_name="comments")

    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_role", table_name="users")

    op.drop_index("ix_issues_reported_by_status", table_name="issues")
    op.drop_index("ix_issues_created_at", table_name="issues")
    op.drop_index("ix_issues_assigned_to", table_name="issues")
    op.drop_index("ix_issues_reported_by", table_name="issues")
    op.drop_index("ix_issues_priority", table_name="issues")
    op.drop_index("ix_issues_category", table_name="issues")
    op.drop_index("ix_issues_status", table_name="issues")

    op.drop_index("ix_api_audit_logs_created_at", table_name="api_audit_logs")
    op.drop_index("ix_api_audit_logs_action", table_name="api_audit_logs")
    op.drop_index("ix_api_audit_logs_user_id", table_name="api_audit_logs")
    op.drop_table("api_audit_logs")

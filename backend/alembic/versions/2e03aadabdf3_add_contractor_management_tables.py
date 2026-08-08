"""add_contractor_management_tables

Revision ID: 2e03aadabdf3
Revises: bcc753702a4e
Create Date: 2026-07-25 05:17:18.691912

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '2e03aadabdf3'
down_revision = 'bcc753702a4e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create contractor_profiles table
    op.create_table('contractor_profiles',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('company_name', sa.String(), nullable=True),
    sa.Column('gst_number', sa.String(), nullable=True),
    sa.Column('license_number', sa.String(), nullable=True),
    sa.Column('specializations', sa.JSON(), nullable=False),
    sa.Column('years_of_experience', sa.Integer(), nullable=True),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('availability_status', sa.Enum('available', 'busy', 'on_leave', 'inactive', name='availabilitystatus'), nullable=False),
    sa.Column('total_jobs_completed', sa.Integer(), nullable=False),
    sa.Column('average_rating', sa.Numeric(precision=3, scale=2), nullable=False),
    sa.Column('total_ratings', sa.Integer(), nullable=False),
    sa.Column('response_time_avg', sa.Integer(), nullable=True),
    sa.Column('completion_rate', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('verified_at', sa.DateTime(), nullable=True),
    sa.Column('verified_by', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('gst_number'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_contractor_profiles_user_id'), 'contractor_profiles', ['user_id'], unique=False)

    # Create contractor_ratings table
    op.create_table('contractor_ratings',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('contractor_id', sa.String(), nullable=False),
    sa.Column('issue_id', sa.String(), nullable=True),
    sa.Column('rated_by', sa.String(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('quality_rating', sa.Integer(), nullable=True),
    sa.Column('punctuality_rating', sa.Integer(), nullable=True),
    sa.Column('professionalism_rating', sa.Integer(), nullable=True),
    sa.Column('review_text', sa.Text(), nullable=True),
    sa.Column('work_photos', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor_profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['rated_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contractor_ratings_contractor_id'), 'contractor_ratings', ['contractor_id'], unique=False)

    # Create work_completions table
    op.create_table('work_completions',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('issue_id', sa.String(), nullable=False),
    sa.Column('contractor_id', sa.String(), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=False),
    sa.Column('work_description', sa.Text(), nullable=True),
    sa.Column('materials_used', sa.JSON(), nullable=True),
    sa.Column('labor_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('total_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('verified_by', sa.String(), nullable=True),
    sa.Column('verified_at', sa.DateTime(), nullable=True),
    sa.Column('verification_notes', sa.Text(), nullable=True),
    sa.Column('before_photos', sa.JSON(), nullable=True),
    sa.Column('after_photos', sa.JSON(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor_profiles.id'], ),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('issue_id')
    )
    op.create_index(op.f('ix_work_completions_contractor_id'), 'work_completions', ['contractor_id'], unique=False)
    op.create_index(op.f('ix_work_completions_issue_id'), 'work_completions', ['issue_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_work_completions_issue_id'), table_name='work_completions')
    op.drop_index(op.f('ix_work_completions_contractor_id'), table_name='work_completions')
    op.drop_table('work_completions')
    
    op.drop_index(op.f('ix_contractor_ratings_contractor_id'), table_name='contractor_ratings')
    op.drop_table('contractor_ratings')
    
    op.drop_index(op.f('ix_contractor_profiles_user_id'), table_name='contractor_profiles')
    op.drop_table('contractor_profiles')

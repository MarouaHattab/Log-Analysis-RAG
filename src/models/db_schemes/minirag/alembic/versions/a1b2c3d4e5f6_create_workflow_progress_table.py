"""Create workflow_progress table for real-time progress tracking

Revision ID: a1b2c3d4e5f6
Revises: 63022d8075be
Create Date: 2026-01-08 19:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '63022d8075be'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('workflow_progress',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workflow_id', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('current_step', sa.String(length=64), nullable=True),
        sa.Column('current_step_number', sa.Integer(), nullable=False),
        sa.Column('total_steps', sa.Integer(), nullable=False),
        sa.Column('step_progress', sa.Float(), nullable=False),
        sa.Column('overall_progress', sa.Float(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workflow_id')
    )
    
    # Create indexes for efficient querying
    op.create_index('idx_workflow_progress_workflow_id', 'workflow_progress', ['workflow_id'], unique=False)
    op.create_index('idx_workflow_progress_project_id', 'workflow_progress', ['project_id'], unique=False)
    op.create_index('idx_workflow_progress_status', 'workflow_progress', ['status'], unique=False)
    op.create_index('idx_workflow_progress_created_at', 'workflow_progress', ['created_at'], unique=False)


def downgrade():
    op.drop_index('idx_workflow_progress_created_at', table_name='workflow_progress')
    op.drop_index('idx_workflow_progress_status', table_name='workflow_progress')
    op.drop_index('idx_workflow_progress_project_id', table_name='workflow_progress')
    op.drop_index('idx_workflow_progress_workflow_id', table_name='workflow_progress')
    op.drop_table('workflow_progress')

"""Add findings and audit_snapshots tables

Revision ID: 0002_add_findings_snapshots
Revises: 0001_initial
Create Date: 2026-08-29
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_add_findings_snapshots'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=False),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_findings_id'), 'findings', ['id'], unique=False)
    op.create_index(op.f('ix_findings_audit_id'), 'findings', ['audit_id'], unique=False)

    # Create audit_snapshots table
    op.create_table(
        'audit_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('snapshot_data', sa.JSON(), nullable=False),
        sa.Column('seo_score', sa.Float(), nullable=True),
        sa.Column('geo_score', sa.Float(), nullable=True),
        sa.Column('category_scores', sa.JSON(), nullable=True),
        sa.Column('finding_counts', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_audit_snapshots_id'), 'audit_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_audit_snapshots_audit_id'), 'audit_snapshots', ['audit_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_snapshots_audit_id'), table_name='audit_snapshots')
    op.drop_index(op.f('ix_audit_snapshots_id'), table_name='audit_snapshots')
    op.drop_table('audit_snapshots')
    op.drop_index(op.f('ix_findings_audit_id'), table_name='findings')
    op.drop_index(op.f('ix_findings_id'), table_name='findings')
    op.drop_table('findings')

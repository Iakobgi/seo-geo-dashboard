"""Establish the schema baseline without replacing existing tables or data."""
from alembic import op
from app.database import Base
from app import models  # Register all application tables with metadata.

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade():
    # Adopting existing tables is deliberately non-destructive in both directions.
    pass

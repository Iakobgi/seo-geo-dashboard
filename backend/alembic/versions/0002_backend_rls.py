"""Restrict Supabase Data API access to FastAPI-owned application tables."""
from pathlib import Path
from alembic import op
from sqlalchemy import text

revision = "0002_backend_rls"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    if connection.dialect.name != "postgresql":
        return
    role = connection.exec_driver_sql(
        "SELECT rolbypassrls OR rolsuper FROM pg_roles WHERE rolname=current_user"
    ).scalar()
    if not role:
        raise RuntimeError("Backend role must bypass RLS before applying backend-only access controls")
    sql_path = Path(__file__).resolve().parents[2] / "sql" / "secure_backend_tables.sql"
    sql = sql_path.read_text(encoding="utf-8").split("BEGIN;", 1)[1].rsplit("COMMIT;", 1)[0]
    connection.execute(text(sql))


def downgrade():
    # Do not silently reopen public Data API access during an application rollback.
    # Restore deliberately from the pre-deployment permission backup if required.
    pass

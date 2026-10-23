-- Applied by Alembic revision 0002_backend_rls; direct execution requires the same role checks.
-- The React app uses FastAPI's own authentication, not Supabase Auth or PostgREST.
-- The backend must connect as the table owner or a role with BYPASSRLS.
-- Deny browser Data API roles access to these backend-only tables.
-- This does not remove rows, alter password hashes, or change backend login credentials.
BEGIN;
DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'alembic_version', 'users', 'audits', 'recommendations', 'keywords',
        'findings', 'audit_snapshots', 'competitors', 'competitor_audits',
        'knowledge_articles', 'optimization_cycles', 'optimization_steps'
    ] LOOP
        IF to_regclass(format('public.%I', table_name)) IS NOT NULL THEN
            EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
            EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE public.%I FROM anon, authenticated', table_name);
        END IF;
    END LOOP;
END $$;
COMMIT;

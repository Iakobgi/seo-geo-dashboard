# Local upgrade and verification — 23 October 2026

## What changed

- New home, account, and workspace design with mobile navigation and keyboard focus states.
- Login preserves the requested destination; registration confirms passwords; recovery never exposes reset tokens.
- Independent SEO/GEO gauges and same-page score history, with workspace totals.
- Audit search, sorting, page metadata, structured findings/evidence, severity filters, and report downloads.
- Recommendation status filters and reliable handling of API failures.
- Every new audit saves actionable recommendations from findings; the configured AI model runs without needing an explicit frontend override.
- AI plan generation reports whether it used OpenRouter or rule-based fallback; generated plans can be downloaded.
- Keyword creation/refresh validates input, duplicates, and audit ownership. The UI explicitly labels the configured simulated provider.
- Fixed audit comparison routing, snapshot score errors, cross-account finding access, and private/IPv6/redirect URL checks in the crawler.
- The landing page no longer loads the dashboard chart bundle.

## Verification

- 98 backend regression tests pass against a disposable SQLite database.
- Frontend TypeScript check and production build pass.
- Local frontend/backend/Supabase readiness verified.
- Signed-in browser verified audit creation, keyword add/refresh, recommendation completion/filtering, audit search/sorting/details, findings expansion, and live OpenRouter plan generation/download.
- QA data is identifiable by the URL query `dashboard-qa=20261023` and keyword `dashboard qa october 2026`. Existing user data was retained.
- Email settings are present, but no live email was sent. Delivery handling was tested with a mocked email service.

## Before deployment

- Supabase protections applied through `0002_backend_rls`: all 12 public tables have RLS enabled; browser Data API roles no longer have table privileges. Backend database access was verified. Pre-change permission metadata is retained locally in the ignored `.backups/` directory.
- Keep `backend/.env` and `frontend/.env` out of version control. The local frontend uses `/api` through Vite; the backend uses the Supabase session pooler with SSL.
- A live search provider is separate from OpenRouter. Current keyword rankings are simulated.
- Verify SMTP delivery and password-reset email delivery before deployment.
- The GitHub workflow deploys the exact tested frontend artifact to Oracle, updates the approved encrypted backend credentials, runs migrations, and checks authentication through Nginx with automatic smoke-test account cleanup.

## Release security checks

- Updated Vite, React Router, and vulnerable transitive dependencies; npm audit reports zero vulnerabilities.
- Schema migrations verified on both the existing Supabase database and a disposable SQLite database.
- GitHub deployment secrets contain only the two explicitly approved backend credentials, encrypted using the repository public key.
- Deployment preserves the previous backend environment and commit reference in an ignored server-local directory.

# SEO/GEO AI Dashboard

An AI-powered SEO & GEO (Generative Engine Optimization) dashboard: audit any URL, get an
SEO score and a GEO score (how well the page is structured for AI answer engines like
ChatGPT/Perplexity), get AI-generated recommendations, track keywords, and run a one-click
"AI Agent" that produces a full optimization plan + rewritten on-page content.

**Stack:** React + TypeScript + Tailwind (frontend) · FastAPI + SQLAlchemy (backend) ·
PostgreSQL · OpenRouter (AI) · Docker · GitHub Actions.

This has been built and tested end-to-end in a sandbox (auth, real URL scraping/scoring,
and a production frontend build all verified working). What's below is exactly how to run
it yourself, and how to ship it to GitHub and a server.

---

## 1. Project structure

```
seo-geo-dashboard/
├── backend/            FastAPI app (auth, scraping, AI scoring, keywords, agent, email)
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/            React + TS + Tailwind dashboard
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml       local dev (builds images from source)
├── docker-compose.prod.yml  production (pulls prebuilt images from Docker Hub)
└── .github/workflows/ci-cd.yml
```

## 2. Prerequisites

- Docker + Docker Compose (recommended path)
- OR locally: Node.js 20+, Python 3.11+, PostgreSQL 15
- A GitHub account
- Optional: an OpenRouter API key (https://openrouter.ai) — without one, the app still
  works fully using a built-in heuristic SEO/GEO scorer (see `app/services/ai_service.py`)
- Optional: SMTP credentials (e.g. SendGrid) if you want email reports

## 3. Run it locally with Docker (fastest path)

```bash
cd seo-geo-dashboard
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit backend/.env: set SECRET_KEY to a long random string, and (optionally) OPENROUTER_API_KEY

docker compose up --build
```

- Frontend: http://localhost
- Backend API docs (Swagger): http://localhost:8000/docs

Create an account from the login screen, then run your first audit from the Dashboard.

## 4. Run it locally without Docker (dev mode)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Point DATABASE_URL at a running Postgres instance, or use sqlite for quick testing:
#   DATABASE_URL=sqlite:///./dev.db
uvicorn app.main:app --reload --port 8000
```

**Frontend** (separate terminal):
```bash
cd frontend
cp .env.example .env       # VITE_API_URL=http://localhost:8000
npm install
npm run dev
```
Visit http://localhost:5173.

## 5. Environment variables reference

`backend/.env`:
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres (or sqlite for local testing) connection string |
| `SECRET_KEY` | JWT signing secret — set a long random value |
| `OPENROUTER_API_KEY` | Optional. Enables real AI scoring/content generation |
| `AI_MODEL` | e.g. `openai/gpt-4o-mini`, `anthropic/claude-3.5-sonnet` |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` / `EMAIL_FROM` | Optional, for emailed reports |
| `FRONTEND_URL` | Used for CORS |
| `DEMO_USER_EMAIL` / `DEMO_AUDIT_URL` | Optional, for the 24h scheduled demo audit job |

`frontend/.env`:
| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Base URL of the backend API |

## 6. Push the project to GitHub

```bash
cd seo-geo-dashboard
git init
git add .
git commit -m "Initial commit: SEO/GEO AI Dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/seo-geo-dashboard.git
git push -u origin main
```

`.env` files are git-ignored by design — never commit real secrets. Only `.env.example`
files are tracked.

## 7. Set up CI/CD (GitHub Actions)

The workflow at `.github/workflows/ci-cd.yml` does three things on every push to `main`:
1. Runs backend Python compile checks and frontend `npm run build` (on every push/PR).
2. Builds and pushes Docker images for backend + frontend to Docker Hub.
3. SSHes into your VPS and redeploys via `docker-compose.prod.yml`.

In your GitHub repo, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | A Docker Hub access token |
| `VITE_API_URL` | Public URL of your backend, e.g. `https://api.yourdomain.com` |
| `VPS_HOST` | Your server's IP or hostname |
| `VPS_USER` | SSH user on the server |
| `VPS_SSH_KEY` | Private SSH key with access to that user (no passphrase) |
| `VPS_PROJECT_PATH` | Path on the server where the repo is checked out, e.g. `/opt/seo-geo-dashboard` |

If you don't want automatic VPS deployment yet, you can leave the `deploy` job's secrets
unset — the build-and-push job will still work and just push images to Docker Hub.

## 8. Deploy to a VPS (manual first-time setup)

```bash
# On your server
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
mkdir -p /opt/seo-geo-dashboard && cd /opt/seo-geo-dashboard

git clone https://github.com/<your-username>/seo-geo-dashboard.git .
cp backend/.env.example backend/.env
nano backend/.env   # fill in SECRET_KEY, OPENROUTER_API_KEY, etc.

export DOCKER_USERNAME=<your-dockerhub-username>
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Put Nginx or Caddy in front of it (recommended) for HTTPS termination — point your domain's
A record at the server, then reverse-proxy `:80` (frontend) and `:8000` (backend) behind
your TLS certs (Let's Encrypt via Certbot or Caddy's automatic HTTPS both work well).

After this first manual setup, every `git push` to `main` will auto-redeploy via the
GitHub Actions workflow above.

## 9. Alternative: Cloudflare Pages (frontend only)

1. In the Cloudflare dashboard, create a Pages project connected to your GitHub repo.
2. Build settings: root directory `frontend`, build command `npm run build`, output
   directory `dist`.
3. Add the environment variable `VITE_API_URL` pointing at your backend (hosted on a VPS,
   Fly.io, Railway, or Render — FastAPI needs a persistent Python process, so it doesn't
   run on Cloudflare Workers/Pages directly without significant rework).

## 10. What's simulated vs. real (be upfront about this in interviews/portfolio)

- **SEO scraping & scoring**: real — it fetches the live page and extracts title, meta
  description, H1/H2s, word count, image/link counts, load time.
- **AI recommendations**: real when `OPENROUTER_API_KEY` is set; otherwise a deterministic
  rule-based fallback so the app is always usable.
- **Keyword rank tracking**: simulated (`app/routes/keywords.py`, `simulate_position()`).
  Wire in a real SERP API (SerpApi, DataForSEO, ValueSERP) to make it real — the function
  is isolated specifically so that's a one-file change.
- **Scheduled audits + email reports**: real, using APScheduler + SMTP.

## 11. Next steps you could add for an even stronger portfolio piece

- Alembic migrations instead of `create_all` (production schema management)
- Real SERP API integration for keyword tracking
- PDF report export (e.g. with `weasyprint`)
- Per-user scheduled tracked URLs instead of one demo URL
- Tests (`pytest` for backend, `vitest` for frontend) + add them to the CI workflow

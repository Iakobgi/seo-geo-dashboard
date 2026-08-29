# SEO/GEO AI Dashboard

An AI-powered SEO & GEO (Generative Engine Optimization) dashboard: audit any URL, get an
SEO score and a GEO score (how well the page is structured for AI answer engines like
ChatGPT/Perplexity/Claude), get AI-generated recommendations, track keywords, run
competitor analysis, and drive an optimization agent with re-audit tracking.

**Stack:** React + TypeScript + Tailwind (frontend) · FastAPI + SQLAlchemy (backend) ·
PostgreSQL (Docker) · OpenRouter (AI) · Docker · GitHub Actions.

All 78 backend tests pass. The production frontend builds cleanly. The full pipeline —
auth, scraping, scoring, recommendations, competitor tracking, and optimization cycles —
is functional.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Oracle Cloud Always Free VPS                            │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  Frontend    │◄──►│   Backend    │◄──►│   PostgreSQL│ │
│  │  (port 80)   │    │  (port 8000) │    │  (port 5432)│ │
│  └──────────────┘    └──────────────┘    └────────────┘ │
│              all inside Docker Compose, managed by CI/CD │
└──────────────────────────────────────────────────────────┘
```

Everything runs on one free Oracle Cloud VM. No external database provider needed.

---

## 1. Prerequisites

- An Oracle Cloud account (free tier, needs card for verification but $0 charge)
- A Docker Hub account
- A GitHub account

---

## 2. Set up Oracle Cloud (VPS)

1. Go to https://oracle.com/cloud/free
2. Sign up (credit card required for identity verification, never charged if within free limits)
3. Create a compute instance:
   - **Compartment**: Always Free
   - **Shape**: ARM (A1 — Always Free, 1 OCPU, 1GB RAM)
   - **Image**: Ubuntu 22.04
   - **Add SSH key**: paste your public key (generated below)
   - **Assign public IP**: Yes
4. Note the **Public IP** — you'll need it throughout the setup

---

## 3. Generate SSH keys (on your Windows PC)

Run this in your Windows terminal (PowerShell or Git Bash):

```bash
ssh-keygen -t ed25519 -C "github-actions-seo-geo" -f ~/.ssh/id_seo_gha -N ""
cat ~/.ssh/id_seo_gha.pub
```

Copy the output (the public key). Add it to your Oracle Cloud instance's SSH keys,
then add the **private key** content to GitHub Secrets as `VPS_SSH_KEY`.

---

## 4. Prepare the server

From your Windows terminal (replace `YOUR_SERVER_IP` with your Oracle Cloud IP):

```bash
ssh root@YOUR_SERVER_IP "bash -s" << 'EOF'
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
mkdir -p /opt/seo-geo-dashboard && cd /opt/seo-geo-dashboard
git clone https://github.com/Iakobgi/seo-geo-dashboard.git .
cp backend/.env.example backend/.env
echo "Server ready. Edit backend/.env before first deploy."
EOF
```

---

## 5. Configure backend/.env on the server

```bash
ssh root@YOUR_SERVER_IP
nano /opt/seo-geo-dashboard/backend/.env
```

At minimum, change:
```
SECRET_KEY=your-long-random-string-here
```

Optional (recommended):
```
OPENROUTER_API_KEY=sk-or-v1-...    # real AI recommendations
FRONTEND_URL=http://YOUR_SERVER_IP # CORS
```

Save and exit (`Ctrl+X`, `Y`, `Enter`).

---

## 6. Add GitHub Secrets

Go to: https://github.com/Iakobgi/seo-geo-dashboard/settings/secrets/actions

| Secret | Value |
|---|---|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token (Docker Hub → Account Settings → Security → New Access Token) |
| `VITE_API_URL` | `http://YOUR_SERVER_IP` |
| `VPS_HOST` | Your Oracle Cloud server IP |
| `VPS_USER` | `root` |
| `VPS_SSH_KEY` | Full private key content (all lines including BEGIN/END) |
| `VPS_PROJECT_PATH` | `/opt/seo-geo-dashboard` |

---

## 7. Trigger the deploy

On your Windows PC:

```bash
cd c:/Users/User/Desktop/omniroute-test/seo-geo-dashboard
git commit --allow-empty -m "trigger CI/CD deploy"
git push origin main
```

Watch the pipeline: https://github.com/Iakobgi/seo-geo-dashboard/actions

---

## 8. What the pipeline does

```
push to main
  ├─ backend-tests     → pytest (78 tests pass)
  ├─ frontend-checks   → npm run build
  ├─ build-and-push    → Docker images → Docker Hub
  └─ deploy            → SSH to VPS → docker compose pull + up
```

---

## 9. Project structure

```
seo-geo-dashboard/
├── backend/
│   ├── app/
│   │   ├── routes/          audits, competitors, keywords, knowledge, optimization
│   │   ├── services/        crawler, seo, geo, schema, eeat, scoring, serp, rag
│   │   └── utils/           security (SSRF protection)
│   ├── tests/               78 pytest tests (all passing)
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.prod.yml  production (PostgreSQL + backend + frontend in Docker)
└── .github/workflows/ci-cd.yml
```

---

## 10. Features

| Feature | Status |
|---------|--------|
| Multi-page crawler (Playwright) | ✅ |
| Structured SEO findings with evidence | ✅ |
| Deterministic weighted scoring | ✅ |
| GEO analysis (6 metrics) | ✅ |
| Schema.org JSON-LD + microdata | ✅ |
| E-E-A-T analysis (5 dimensions) | ✅ |
| Competitor analysis | ✅ |
| SERP abstraction (Simulated/SerpApi/DataForSEO) | ✅ |
| RAG knowledge base (12 articles) | ✅ |
| Evidence-based AI recommendations | ✅ |
| Optimization cycles with re-audit | ✅ |
| SSRF protection | ✅ |
| 78 pytest tests | ✅ |
| CI/CD (tests + Docker push + SSH deploy) | ✅ |

---

## 11. Roadmap

- [ ] pgvector semantic search for RAG
- [ ] Real SERP API integration (SerpApi / DataForSEO)
- [ ] PDF report export
- [ ] Frontend component tests (Vitest)
- [ ] Per-user scheduled tracked URLs

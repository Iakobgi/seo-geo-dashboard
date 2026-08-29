# SEO/GEO AI Dashboard

An AI-powered SEO & GEO (Generative Engine Optimization) dashboard: audit any URL, get an
SEO score and a GEO score (how well the page is structured for AI answer engines like
ChatGPT/Perplexity/Claude), get AI-generated recommendations, track keywords, run
competitor analysis, and drive an optimization agent with re-audit tracking.

**Stack:** React + TypeScript + Tailwind (frontend) · FastAPI + SQLAlchemy (backend) ·
PostgreSQL (Supabase free tier) · OpenRouter (AI) · Docker · GitHub Actions.

All 78 backend tests pass. The production frontend builds cleanly. The full pipeline —
auth, scraping, scoring, recommendations, competitor tracking, and optimization cycles —
is functional.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Oracle Cloud Always Free VM (1 OCPU, 1GB RAM)                  │
│  ┌──────────────┐    ┌──────────────┐                         │
│  │  Frontend    │◄──►│   Backend    │                         │
│  │  (port 80)   │    │  (port 8000) │                         │
│  └──────────────┘    └──────┬───────┘                         │
│                             │                                  │
│                      Internet (HTTPS)                           │
│                             │                                  │
│                      Supabase (Free Tier)                       │
│                     PostgreSQL 15                              │
└─────────────────────────────────────────────────────────────────┘
```

- **Backend + Frontend**: Docker containers on Oracle Cloud free VM
- **Database**: Supabase managed PostgreSQL (free tier: 500MB, no card needed)
- **CI/CD**: GitHub Actions builds Docker images → pushes to Docker Hub → deploys to VPS via SSH

---

## 1. Prerequisites

- An Oracle Cloud account (free tier, needs card for verification but $0 charge)
- A Supabase account (free tier, no card needed)
- A Docker Hub account
- A GitHub account

---

## 2. Set up Supabase (database)

1. Go to https://supabase.com and create a free account
2. Click **New Project**
3. Fill in:
   - **Name**: `seo-geo-dashboard`
   - **Database Password**: generate a strong random password (save it — you'll need it)
   - **Region**: choose the closest to your target users
   - **Subscription**: Free (perpetual)
4. Click **Create new project**
5. Wait for provisioning (takes about 2 minutes)
6. Go to **Settings** → **Database**
7. Copy the **Connection string** (it looks like `postgresql://postgres.YOURPROJECT:YOURPASSWORD@aws-0-eu-central-1.pooler.supabase.com:5432/postgres`)
8. Save this string — you'll paste it into the `.env` file on the server

---

## 3. Set up Oracle Cloud (VPS)

1. Go to https://cloud.oracle.com/ and sign in
2. Click the hamburger menu (top left) → **Compute** → **Instances**
3. Click **Create Instance**
4. Fill in:
   - **Name**: `seo-backend`
   - **Compartment**: select your compartment (or create one named `seo-geo`)
   - **Availability Domain**: leave default
   - **Shape**: click **Change Shape** → select **VM.Standard.E2.1.Micro** (Always Free, 1 OCPU, 1GB RAM)
   - **Image**: Oracle Linux 9 (or Ubuntu 22.04)
   - **Networking**: leave defaults — the form will auto-create a VCN and public subnet
   - **Public IPv4 address**: select **Assign a public IPv4 address**
   - **SSH Keys**: click **Paste Public Key** → paste this key:
     ```
     ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGUKq1xUG+cNQYdDEIuR0SPnBN2Qtpt9V+PctRKi2vmk github-actions-seo-geo
     ```
     Then click **Add**
5. Leave all other options (Shielded Instance, Storage, etc.) at their defaults
6. Click **Create**
7. Wait for the instance to reach **Running** status (green checkmark)
8. Note the **Public IP address** shown on the instance page

---

## 4. Prepare the server

SSH into your server from your Windows terminal (replace `YOUR_SERVER_IP`):

```bash
ssh root@YOUR_SERVER_IP
```

Then run these commands on the server:

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker root

# Clone the project
git clone https://github.com/Iakobgi/seo-geo-dashboard.git /opt/seo-geo-dashboard
cd /opt/seo-geo-dashboard

# Create .env from example and edit it
cp backend/.env.example backend/.env
nano backend/.env
```

In the `.env` file, update these values:
- **DATABASE_URL**: paste your Supabase connection string from step 2
- **SECRET_KEY**: generate a long random string (e.g., use `openssl rand -base64 32`)
- **FRONTEND_URL**: `http://YOUR_SERVER_IP`
- **OPENROUTER_API_KEY**: optional, for real AI recommendations

Save and exit (`Ctrl+X`, `Y`, `Enter`).

---

## 5. Add GitHub Secrets

Go to: https://github.com/Iakobgi/seo-geo-dashboard/settings/secrets/actions

Add these secrets:

| Secret | Value |
|---|---|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token (Docker Hub → Account Settings → Security → New Access Token) |
| `VITE_API_URL` | `http://YOUR_SERVER_IP` |
| `VPS_HOST` | Your Oracle Cloud server IP |
| `VPS_USER` | `root` |
| `VPS_SSH_KEY` | Full private key content (the file at `~/.ssh/id_seo_gha` — copy all lines including BEGIN/END) |
| `VPS_PROJECT_PATH` | `/opt/seo-geo-dashboard` |

---

## 6. Trigger the deploy

On your Windows PC:

```bash
cd c:/Users/User/Desktop/omniroute-test/seo-geo-dashboard
git commit --allow-empty -m "trigger CI/CD deploy"
git push origin main
```

Watch the pipeline: https://github.com/Iakobgi/seo-geo-dashboard/actions

---

## 7. What the pipeline does

```
push to main
  ├─ backend-tests      → pytest (78 tests pass)
  ├─ frontend-checks    → npm run build
  ├─ build-and-push     → Docker images → Docker Hub
  └─ deploy             → SSH to VPS → docker compose pull + up
```

---

## 8. Project structure

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
├── docker-compose.prod.yml  production (backend + frontend, Supabase for DB)
└── .github/workflows/ci-cd.yml
```

---

## 9. Features

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

## 10. Oracle Cloud Always Free limits

| Resource | Limit | Your Usage |
|----------|-------|------------|
| Compute | 2 ARM VMs (1 OCPU, 1GB RAM each) | 1 VM ✅ |
| Storage | 200GB block storage | ~10GB ✅ |
| Bandwidth | 10TB egress/month | Light traffic ✅ |

As long as you stay on the VM.Standard.E2.1.Micro shape and don't add extra services, you'll stay within free limits.

---

## 11. Troubleshooting

- **PostgreSQL connection errors**: check DATABASE_URL in backend/.env — make sure it matches your Supabase connection string exactly
- **Port 80 or 8000 not accessible**: check Oracle Cloud firewall rules — allow inbound TCP on ports 80 and 8000
- **SSH key rejected**: make sure you pasted the full public key including `ssh-ed25519` prefix
- **Build fails in CI**: check the Actions tab for error logs — most failures are due to missing environment variables

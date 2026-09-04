# SEO/GEO AI Dashboard

An AI-powered SEO & GEO (Generative Engine Optimization) dashboard: audit any URL, get an
SEO score and a GEO score (how well the page is structured for AI answer engines like
ChatGPT/Perplexity/Claude), get AI-generated recommendations, track keywords, run
competitor analysis, and drive an optimization agent with re-audit tracking.

**Stack:** React + TypeScript + Tailwind (frontend) · FastAPI + SQLAlchemy on Python 3.11
(backend, runs as a systemd service) · PostgreSQL via Supabase Session Pooler over IPv4 ·
OpenRouter (AI) · Nginx · GitHub Actions (SSH deploy).

Live app: **http://141.145.220.152**

All 78 backend tests pass. The production frontend builds cleanly. The full pipeline —
auth, scraping, scoring, recommendations, competitor tracking, and optimization cycles —
is functional.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Oracle Cloud Always Free A1 ARM VM (4 OCPU, 6 GB RAM)               │
│  Ubuntu 22.04 · Python 3.11                                         │
│                                                                      │
│  ┌──────────────────┐        ┌─────────────────────┐               │
│  │  Nginx           │  proxy  │  FastAPI backend    │               │
│  │  /               │ ──────► │  systemd: seo-backend│              │
│  │  (port 80)       │  /api   │  (port 8000)        │               │
│  │  serves SPA      │ ──────► │                     │               │
│  └──────────────────┘        └──────────┬──────────┘               │
│                                         │                           │
└─────────────────────────────────────────┼───────────────────────────┘
                                          │  IPv4 Session Pooler
                                          ▼
                              ┌─────────────────────────┐
                              │  Supabase PostgreSQL    │
                              │  aws-...pooler.supabase │
                              │  .com:5432              │
                              └─────────────────────────┘
```

- **Hosting**: single Oracle Cloud A1 ARM instance (Always Free, Ampere A1, 6 GB RAM)
- **Database**: Supabase managed PostgreSQL connected via the **Session Pooler over IPv4**
  (the Always Free A1 VM only has IPv6 outbound, so the direct connection string won't
  resolve — the pooler gives us a stable IPv4 endpoint)
- **Backend**: FastAPI on Python 3.11, managed by a `seo-backend` systemd service
- **Frontend**: React/Vite build served by Nginx on port 80, reverse-proxying `/api/*`
  to the backend on `127.0.0.1:8000`
- **CI/CD**: GitHub Actions runs tests + builds the frontend, then deploys over **SSH**
  to the VM (no Docker Hub, no containers — just `git pull` + `npm run build` +
  `alembic upgrade head` + `systemctl restart seo-backend`)

---

## 1. Prerequisites

- An Oracle Cloud account (free tier, card required for verification but $0 charge)
- A Supabase account (free tier)
- A GitHub account
- An SSH key pair for GitHub Actions (added as `VPS_SSH_KEY`)

---

## 2. Set up Supabase (database)

1. Go to https://supabase.com and create a free account
2. Click **New Project**
3. Fill in:
   - **Name**: `seo-geo-dashboard`
   - **Database Password**: generate a strong random password (save it)
   - **Region**: pick one close to your VM (e.g. `eu-central-1`)
   - **Subscription**: Free
4. Click **Create new project** and wait for provisioning (~2 minutes)
5. Go to **Settings** → **Database**
6. Under **Connection string**, select **Session pooler** (NOT "Direct connection") and
   copy the URI. It looks like:
   ```
   postgresql://postgres.YOURPROJECT:YOURPASSWORD@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
   ```
   > The Session Pooler is required because the Oracle A1 ARM instance has IPv6-only
   > outbound and the direct Supabase endpoint is IPv6.
7. Save this string — you'll paste it into `backend/.env` on the server

---

## 3. Provision the Oracle Cloud A1 ARM VM

1. Go to https://cloud.oracle.com/ and sign in
2. Hamburger menu → **Compute** → **Instances** → **Create Instance**
3. Fill in:
   - **Name**: `seo-backend`
   - **Image**: Ubuntu 22.04 (or Oracle Linux 9)
   - **Shape**: click **Change Shape** → **Ampere** → **VM.Standard.A1.Flex**
     with **4 OCPU** and **6 GB RAM** (still Always Free, total 4 OCPU / 24 GB per tenancy)
   - **Networking**: leave defaults; auto-creates a VCN + public subnet
   - **Public IPv4 address**: **Assign a public IPv4 address**
   - **SSH Keys**: **Paste Public Key** — paste the public key whose private counterpart
     you'll use as `VPS_SSH_KEY`. Then click **Add**
4. Leave Shielded Instance / Storage at defaults → **Create**
5. Wait for **Running** status, then note the **Public IP** (e.g. `141.145.220.152`)
6. In the VCN's **Security List**, open ingress TCP **80** (and optionally **22** if you
   want SSH restricted) to `0.0.0.0/0`

---

## 4. Prepare the server

SSH in (replace `YOUR_SERVER_IP`):

```bash
ssh ubuntu@YOUR_SERVER_IP
```

Then run on the server (Ubuntu):

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip \
    nodejs npm nginx git

# Clone the project into the home directory (matches GitHub Actions VPS_PROJECT_PATH)
git clone https://github.com/Iakobgi/seo-geo-dashboard.git ~/seo-geo-dashboard
cd ~/seo-geo-dashboard

cp backend/.env.example backend/.env
nano backend/.env
```

Fill in `backend/.env`:

- **DATABASE_URL** — the Session Pooler string from step 2
- **SECRET_KEY** — `openssl rand -base64 32`
- **FRONTEND_URL** — `http://YOUR_SERVER_IP`
- **OPENROUTER_API_KEY** — optional, for real AI recommendations

Save and exit.

#### Install backend deps and run migrations

```bash
python3.11 -m pip install --user -r backend/requirements.txt
cd ~/seo-geo-dashboard/backend
PYTHONPATH=. python3.11 -m alembic upgrade head
cd ~
```

#### Create the systemd service (`seo-backend`)

```bash
sudo tee /etc/systemd/system/seo-backend.service > /dev/null <<'EOF'
[Unit]
Description=SEO/GEO Dashboard FastAPI backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/seo-geo-dashboard/backend
EnvironmentFile=/home/ubuntu/seo-geo-dashboard/backend/.env
Environment=PYTHONPATH=/home/ubuntu/seo-geo-dashboard/backend
ExecStart=/usr/bin/python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now seo-backend
sudo systemctl status seo-backend   # should show active (running)
```

#### Install Playwright (used by the crawler)

```bash
python3.11 -m playwright install --with-deps chromium
```

#### Configure Nginx

```bash
sudo cp ~/seo-geo-dashboard/frontend/nginx.conf /etc/nginx/conf.d/default.conf
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```

The frontend nginx config proxies `/api/*` to `http://127.0.0.1:8000`, so the React
build talks to the backend via the same origin (no CORS hassle).

Open a quick sanity check from your laptop:

```bash
curl http://YOUR_SERVER_IP/api/health
```

You should get a JSON `{"status":"ok",...}`.

---

## 5. Add GitHub Secrets

Go to: https://github.com/Iakobgi/seo-geo-dashboard/settings/secrets/actions

| Secret | Value |
|---|---|
| `VPS_HOST` | `141.145.220.152` (or your Oracle public IP) |
| `VPS_USER` | `ubuntu` (or `opc` for Oracle Linux) — **not `root`** |
| `VPS_SSH_KEY` | Full private key contents (BEGIN/END lines included) for the public key you pasted at VM creation |
| `VPS_PROJECT_PATH` | `/home/ubuntu/seo-geo-dashboard` (must match `~`) |
| `VITE_API_URL` | (not required when nginx reverse-proxies — the build defaults to same-origin `/api`) |

> No `DOCKER_USERNAME` / `DOCKER_PASSWORD` needed anymore — the pipeline no longer
> builds or pushes container images.

---

## 6. Trigger the deploy

From your local machine:

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
  ├─ backend-tests      → pytest (Python 3.11, 78 tests pass)
  ├─ frontend-checks    → npm ci + npm run build
  └─ deploy (needs tests)
       └─ appleboy/ssh-action → VPS
            ├─ git pull origin main
            ├─ ensure nginx + copy nginx.conf + reload
            ├─ pip install --user backend/requirements.txt
            ├─ npm ci && VITE_API_URL=... && npm run build
            ├─ publish dist/ to /usr/share/nginx/html/
            ├─ alembic upgrade head
            └─ systemctl restart seo-backend   (or start on first deploy)
```

No Docker, no Docker Hub, no image pulls — just SSH, git, pip, npm, and systemd.

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
│   └── Dockerfile           (kept for reference, not used in deploy)
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── .env.example
│   ├── nginx.conf           (prod nginx site config; reverse-proxies /api → :8000)
│   └── Dockerfile           (kept for reference, not used in deploy)
├── docker-compose.prod.yml  (legacy, not used — A1 deploy is systemd + nginx)
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
| CI/CD (tests + SSH deploy via GitHub Actions) | ✅ |

---

## 10. Oracle Cloud Always Free limits

| Resource | Limit | Your Usage |
|----------|-------|------------|
| Compute (ARM A1) | 4 OCPU, 24 GB RAM total per tenancy | 4 OCPU, 6 GB RAM ✅ |
| Block storage | 200 GB total | ~10 GB ✅ |
| Bandwidth | 10 TB egress / month | Light traffic ✅ |

As long as the total A1 allocation across all your VMs stays ≤ 4 OCPU / 24 GB RAM,
you remain in the Always Free tier.

---

## 11. Troubleshooting

- **PostgreSQL connection errors / `could not translate host name`**:
  you pasted the *direct* connection string. Switch to the **Session pooler** string in
  Supabase → Settings → Database (the A1 VM only has IPv6 outbound, and the pooler gives
  you a stable IPv4 endpoint on port 5432).
- **`421 Misdirected Request` or 502 from nginx**: the backend isn't running. Check
  `sudo systemctl status seo-backend` and `journalctl -u seo-backend -e`.
- **`/api/*` returns 404**: nginx config wasn't reloaded. `sudo nginx -t &&
  sudo systemctl reload nginx`, and confirm `/etc/nginx/conf.d/default.conf` matches
  `frontend/nginx.conf` in the repo.
- **SSH key rejected by GitHub Actions**: the public key pasted at VM creation must
  match the private key in the `VPS_SSH_KEY` secret. `ssh -i ~/.ssh/id_xxx ubuntu@IP`
  from your laptop to verify it works locally first.
- **Build fails in CI**: check the Actions tab; most failures are missing secrets or a
  diverged `VPS_PROJECT_PATH` between the secret and the repo path on the VM.
- **Playwright missing browsers on the server**: re-run
  `python3.11 -m playwright install --with-deps chromium`.
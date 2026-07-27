import asyncio
import atexit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routes import auth, audits, recommendations, keywords, agent, reports
from app.services.audit_service import perform_audit
from app.services.email_service import send_report_email
from app import models

app = FastAPI(title="SEO/GEO AI Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(audits.router)
app.include_router(recommendations.router)
app.include_router(keywords.router)
app.include_router(agent.router)
app.include_router(reports.router)

# Create tables on startup (use Alembic migrations in real production instead).
Base.metadata.create_all(bind=engine)


def scheduled_audit_job():
    """Runs on an interval: audits a demo/tracked URL and emails the report.
    In a multi-tenant production app, loop over all users' saved tracked URLs instead."""
    if not settings.DEMO_USER_EMAIL or not settings.DEMO_AUDIT_URL:
        return
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == settings.DEMO_USER_EMAIL).first()
        if not user:
            return
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audit = loop.run_until_complete(perform_audit(settings.DEMO_AUDIT_URL, user.id, db))
        loop.close()
        report = (
            f"Scheduled audit for {audit.url}\n"
            f"SEO Score: {audit.seo_score}\nGEO Score: {audit.geo_score}\n"
        )
        send_report_email(user.email, report, subject="Scheduled SEO Audit Report")
    finally:
        db.close()


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_audit_job, "interval", hours=24, id="daily_audit")
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))


@app.get("/")
def root():
    return {"message": "SEO/GEO AI Dashboard API", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}

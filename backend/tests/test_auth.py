import os
import tempfile
from pathlib import Path

_database_file = Path(tempfile.mkstemp(suffix=".db")[1])
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_database_file.as_posix()}"
os.environ["SECRET_KEY"] = "test-auth-secret"
os.environ["FRONTEND_URL"] = "http://testserver"
os.environ["DEMO_USER_EMAIL"] = ""
os.environ["DEMO_AUDIT_URL"] = ""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    from app.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_register_login_and_me(client):
    email = "user@example.com"
    password = "TestPass123!"

    register_response = client.post(
        "/auth/register", json={"email": email, "password": password}
    )

    assert register_response.status_code == 200
    assert register_response.json()["email"] == email

    login_response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    me_response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email


def test_login_rejects_invalid_password(client):
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "TestPass123!"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_registration_rejects_duplicate_email(client):
    payload = {"email": "user@example.com", "password": "TestPass123!"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


def test_readiness_checks_database(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_hides_database_connection_details(client):
    from unittest.mock import patch
    from sqlalchemy.exc import OperationalError

    with patch("app.main.engine") as engine:
        engine.connect.side_effect = OperationalError(
            "connect", {}, Exception("private connection details")
        )
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


def test_password_recovery_never_exposes_token_when_email_fails(client):
    from unittest.mock import patch

    client.post('/auth/register', json={'email': 'recovery@example.com', 'password': 'StrongPass123!'})
    with patch('app.routes.auth.send_report_email', return_value=False):
        existing = client.post('/auth/password-reset-request', json={'email': 'recovery@example.com'})
        unknown = client.post('/auth/password-reset-request', json={'email': 'unknown@example.com'})
    assert existing.status_code == unknown.status_code == 200
    assert existing.json() == unknown.json()
    assert 'token' not in existing.json()


@pytest.mark.parametrize('password', ['short', 'x' * 73])
def test_registration_validates_password_length(client, password):
    response = client.post('/auth/register', json={'email': 'length@example.com', 'password': password})
    assert response.status_code == 422


def test_reset_requires_strong_password_and_token_is_single_use(client):
    from unittest.mock import patch
    from app.database import SessionLocal
    from app import models

    email = 'reset@example.com'
    client.post('/auth/register', json={'email': email, 'password': 'OriginalPass123!'})
    with patch('app.routes.auth.send_report_email', return_value=True):
        client.post('/auth/password-reset-request', json={'email': email})
    with SessionLocal() as db:
        token = db.query(models.User).filter_by(email=email).one().password_reset_token
    weak = client.post('/auth/password-reset', json={'token': token, 'new_password': 'short'})
    assert weak.status_code == 422
    payload = {'token': token, 'new_password': 'Replacement123!'}
    assert client.post('/auth/password-reset', json=payload).status_code == 200
    assert client.post('/auth/password-reset', json=payload).status_code == 400
    assert client.post('/auth/login', json={'email': email, 'password': 'Replacement123!'}).status_code == 200


def test_audit_routes_protect_findings_and_handle_snapshots(client):
    from app.database import SessionLocal
    from app import models

    headers = []
    for email in ['owner@example.com', 'other@example.com']:
        payload = {'email': email, 'password': 'StrongPass123!'}
        client.post('/auth/register', json=payload)
        token = client.post('/auth/login', json=payload).json()['access_token']
        headers.append({'Authorization': f'Bearer {token}'})
    with SessionLocal() as db:
        owner = db.query(models.User).filter_by(email='owner@example.com').one()
        audit = models.Audit(user_id=owner.id, url='https://example.com', seo_score=40, geo_score=0)
        db.add(audit)
        db.flush()
        finding = models.Finding(audit_id=audit.id, category='content', severity='high', url=audit.url, title='Missing content', description='Example', recommendation='Add content')
        db.add(finding)
        db.add(models.AuditSnapshot(audit_id=audit.id, snapshot_data={}, category_scores={'content': 40}))
        db.commit()
        audit_id, finding_id = audit.id, finding.id
    path = f'/audits/{audit_id}/findings/{finding_id}'
    assert client.get(path, headers=headers[0]).status_code == 200
    assert client.get(path, headers=headers[1]).status_code == 404
    scores = client.get(f'/audits/{audit_id}/scores', headers=headers[0])
    assert scores.status_code == 200
    assert scores.json()['finding_counts']['high'] == 1
    compare = client.get('/audits/compare', params={'audit_id_1': audit_id, 'audit_id_2': audit_id}, headers=headers[0])
    assert compare.status_code == 200
    assert compare.json()['geo_score_change'] == 0
    assert client.get('/audits/compare', params={'audit_id_1': audit_id, 'audit_id_2': audit_id}, headers=headers[1]).status_code == 404


def _login_headers(client):
    payload = {'email': 'qa@example.com', 'password': 'StrongPass123!'}
    client.post('/auth/register', json=payload)
    token = client.post('/auth/login', json=payload).json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_default_audit_saves_actionable_recommendations_without_ai(client):
    from unittest.mock import AsyncMock, patch
    from app.services.crawler_service import CrawlResult, CrawledPage

    headers = _login_headers(client)
    page = CrawledPage(url='https://example.com/', status_code=200, title='Example', word_count=4, html='<html><title>Example</title><body>Short page</body></html>')
    crawl = CrawlResult(start_url=page.url, pages=[page], pages_crawled=1)
    with patch('app.services.audit_service.CrawlerService.crawl', new=AsyncMock(return_value=crawl)), patch('app.services.audit_service.settings.OPENROUTER_API_KEY', None):
        response = client.post('/audits/', json={'url': page.url}, headers=headers)
    assert response.status_code == 200
    recommendations = response.json()['recommendations']
    assert recommendations
    assert len({r['suggestion'] for r in recommendations}) == len(recommendations)
    rec = recommendations[0]
    assert client.patch(f"/recommendations/{rec['id']}/apply", headers=headers).json()['status'] == 'applied'
    assert client.patch(f"/recommendations/{rec['id']}/dismiss", headers=headers).json()['status'] == 'dismissed'


def test_unreadable_page_returns_actionable_error(client):
    from unittest.mock import AsyncMock, patch
    from app.services.crawler_service import CrawlResult

    headers = _login_headers(client)
    with patch('app.services.audit_service.CrawlerService.crawl', new=AsyncMock(return_value=CrawlResult(start_url='https://example.com/'))):
        response = client.post('/audits/', json={'url': 'https://example.com/'}, headers=headers)
    assert response.status_code == 400
    assert 'No readable pages' in response.json()['detail']


def test_keyword_validation_and_provider(client):
    headers = _login_headers(client)
    assert client.get('/keywords/provider', headers=headers).json()['simulated'] is True
    assert client.post('/keywords/', json={'keyword': '   '}, headers=headers).status_code == 400
    assert client.post('/keywords/', json={'keyword': 'term', 'audit_id': 99999}, headers=headers).status_code == 404
    first = client.post('/keywords/', json={'keyword': 'test term'}, headers=headers)
    assert first.status_code == 200
    assert client.post('/keywords/', json={'keyword': ' TEST TERM '}, headers=headers).status_code == 400
    assert client.post(f"/keywords/{first.json()['id']}/refresh", headers=headers).status_code == 200


@pytest.mark.asyncio
async def test_ai_response_sources_and_invalid_payloads():
    from unittest.mock import AsyncMock, patch
    import httpx
    from app.services.ai_service import call_openrouter

    request = httpx.Request('POST', 'https://example.com/chat/completions')
    for response, expected in [
        (httpx.Response(200, request=request, json={'choices': [{'message': {'content': '{"suggestions": ["Improve the title"], "generated_content": {"title": "Example"}}'}}]}), 'openrouter'),
        (httpx.Response(200, request=request, json={'choices': [{'message': {'content': '{"suggestions": "invalid"}'}}]}), 'rules'),
        (httpx.Response(401, request=request, json={'error': 'private provider detail'}), 'rules'),
    ]:
        mock_client = AsyncMock()
        mock_client.post.return_value = response
        with patch('app.services.ai_service.settings.OPENROUTER_API_KEY', 'test-key'), patch('app.services.ai_service.httpx.AsyncClient') as factory:
            factory.return_value.__aenter__.return_value = mock_client
            result = await call_openrouter({'url': 'https://example.com/'})
        assert result['generation_source'] == expected
        assert 'private provider detail' not in str(result)


def test_agent_target_validation(client):
    headers = _login_headers(client)
    assert client.post('/agent/optimize', json={'url': 'https://example.com/', 'target_score': 101}, headers=headers).status_code == 422


def test_audit_delete_is_scoped_and_cascades_to_recommendations(client):
    from app.database import SessionLocal
    from app import models

    headers = _login_headers(client)
    with SessionLocal() as db:
        user = db.query(models.User).filter_by(email='qa@example.com').one()
        audit = models.Audit(user_id=user.id, url='https://example.com/')
        db.add(audit)
        db.flush()
        db.add(models.Recommendation(audit_id=audit.id, suggestion='Test-only recommendation'))
        db.commit()
        audit_id = audit.id
    assert client.delete(f'/audits/{audit_id}').status_code in (401, 403)
    assert client.delete(f'/audits/{audit_id}', headers=headers).status_code == 200
    assert client.get(f'/audits/{audit_id}', headers=headers).status_code == 404
    with SessionLocal() as db:
        assert db.query(models.Recommendation).filter_by(audit_id=audit_id).count() == 0


def test_email_report_does_not_claim_delivery_when_unconfigured(client):
    from unittest.mock import patch
    from app.database import SessionLocal
    from app import models

    headers = _login_headers(client)
    with SessionLocal() as db:
        user = db.query(models.User).filter_by(email='qa@example.com').one()
        audit = models.Audit(user_id=user.id, url='https://example.com/')
        db.add(audit)
        db.commit()
        audit_id = audit.id
    with patch('app.routes.reports.send_report_email', return_value=False):
        response = client.post(f'/reports/audit/{audit_id}/email', headers=headers)
    assert response.status_code == 200
    assert response.json()['emailed'] is False

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    created_at: datetime


# ---- Recommendation ----
class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    suggestion: str
    status: str
    created_at: datetime


# ---- Audit ----
class AuditCreate(BaseModel):
    url: str
    model: Optional[str] = None


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: Optional[str] = None
    h2: Optional[List[str]] = None
    word_count: int
    images_count: int
    links_count: int
    load_time: Optional[float] = None
    seo_score: float
    geo_score: float
    created_at: datetime
    recommendations: List[RecommendationOut] = []


class AuditDetail(AuditOut):
    raw_html: Optional[str] = None


# ---- Findings and scoring ----
class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    audit_id: int
    category: str
    severity: str
    url: str
    title: str
    description: str
    evidence: Optional[Dict[str, Any]] = None
    recommendation: str
    impact_score: float
    created_at: datetime


class CategoryScoreOut(BaseModel):
    category: str
    score: float
    weight: float
    checks_count: int
    passed_checks: int
    failed_checks: int
    important_findings: List[str] = []


class ScoreBreakdownOut(BaseModel):
    overall_score: float
    categories: List[CategoryScoreOut]
    formula: str
    finding_counts: Dict[str, int]


class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 10
    max_depth: int = 2
    respect_robots: bool = True


class CrawledPageOut(BaseModel):
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: Optional[str] = None
    h2: List[str] = []
    h3: List[str] = []
    word_count: int = 0
    images_count: int = 0
    links_count: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    load_time: Optional[float] = None
    canonical_url: Optional[str] = None
    noindex: bool = False
    nofollow: bool = False


class CrawlResultOut(BaseModel):
    start_url: str
    pages_crawled: int
    pages: List[CrawledPageOut]
    broken_internal_links: List[str] = []
    duplicate_titles: Dict[str, List[str]] = {}
    duplicate_meta_descriptions: Dict[str, List[str]] = {}
    robots_txt_found: bool = False
    sitemap_urls: List[str] = []
    crawl_duration: float


# ---- Keyword ----
class KeywordCreate(BaseModel):
    keyword: str
    audit_id: Optional[int] = None


class KeywordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    keyword: str
    position: Optional[int] = None
    previous_position: Optional[int] = None
    volume: Optional[int] = None
    created_at: datetime


# ---- Agent ----
class AgentRequest(BaseModel):
    url: str
    target_score: int = 90
    model: Optional[str] = None


class AgentResult(BaseModel):
    status: str
    audit_id: int
    current_seo_score: float
    current_geo_score: float
    actions: List[str] = []
    generated_content: Optional[Dict[str, Any]] = None

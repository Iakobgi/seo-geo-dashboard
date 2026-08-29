from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    password_reset_token = Column(String, nullable=True, unique=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    audits = relationship("Audit", back_populates="user", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="user", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="user", cascade="all, delete-orphan")


class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)
    h1 = Column(String, nullable=True)
    h2 = Column(JSON, nullable=True)
    word_count = Column(Integer, default=0)
    images_count = Column(Integer, default=0)
    links_count = Column(Integer, default=0)
    load_time = Column(Float, nullable=True)
    seo_score = Column(Float, default=0)
    geo_score = Column(Float, default=0)
    raw_html = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audits")
    recommendations = relationship("Recommendation", back_populates="audit", cascade="all, delete-orphan")
    optimization_cycles = relationship("OptimizationCycle", back_populates="user", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="audit")
    findings = relationship("Finding", back_populates="audit", cascade="all, delete-orphan")
    snapshots = relationship("AuditSnapshot", back_populates="audit", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    type = Column(String, default="suggestion")  # suggestion | generated_content
    suggestion = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending | applied | dismissed
    created_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("Audit", back_populates="recommendations")


class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=True)
    keyword = Column(String, nullable=False)
    position = Column(Integer, nullable=True)
    previous_position = Column(Integer, nullable=True)
    volume = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="keywords")
    audit = relationship("Audit", back_populates="keywords")


class Finding(Base):
    """Structured SEO/GEO finding with category, severity, and evidence."""
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    category = Column(String, nullable=False)  # title_meta, content, links, images, performance, structured_data, indexability, geo
    severity = Column(String, nullable=False)  # critical, high, medium, low, pass
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)  # Actual data found during analysis
    recommendation = Column(Text, nullable=False)
    impact_score = Column(Float, default=0.0)  # 0-10 scale
    created_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("Audit", back_populates="findings")


class AuditSnapshot(Base):
    """Snapshot of audit data for history and comparison."""
    __tablename__ = "audit_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    snapshot_data = Column(JSON, nullable=False)  # Full audit state including findings
    seo_score = Column(Float, default=0)
    geo_score = Column(Float, default=0)
    category_scores = Column(JSON, nullable=True)  # Per-category score breakdown
    finding_counts = Column(JSON, nullable=True)  # {critical: N, high: N, medium: N, low: N}
    created_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("Audit", back_populates="snapshots")


class Competitor(Base):
    """Competitor site to track and compare against."""
    __tablename__ = "competitors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audits")
    competitor_audits = relationship("CompetitorAudit", back_populates="competitor", cascade="all, delete-orphan")


class CompetitorAudit(Base):
    """Audit result for a competitor."""
    __tablename__ = "competitor_audits"
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    seo_score = Column(Float, default=0)
    geo_score = Column(Float, default=0)
    findings_snapshot = Column(JSON, nullable=True)  # Summary of findings
    crawled_at = Column(DateTime, default=datetime.utcnow)

    competitor = relationship("Competitor", back_populates="competitor_audits")


class KnowledgeArticle(Base):
    """Curated SEO/GEO knowledge article with embedding for RAG retrieval."""
    __tablename__ = "knowledge_articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)  # seo, geo, schema, eeat, performance, etc.
    source = Column(String, nullable=True)  # e.g., "google-guidelines", "industry-research"
    embedding = Column(JSON, nullable=True)  # Vector embedding (pgvector-compatible)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OptimizationCycle(Base):
    """Tracks an optimization cycle: baseline → changes → re-audit."""
    __tablename__ = "optimization_cycles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    target_score = Column(Integer, nullable=False)
    baseline_seo_score = Column(Float, nullable=True)
    baseline_geo_score = Column(Float, nullable=True)
    current_seo_score = Column(Float, nullable=True)
    current_geo_score = Column(Float, nullable=True)
    status = Column(String, default="planned")  # planned | in_progress | completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    steps = relationship("OptimizationStep", back_populates="cycle", cascade="all, delete-orphan")


class OptimizationStep(Base):
    """Individual step in an optimization cycle."""
    __tablename__ = "optimization_steps"
    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("optimization_cycles.id"), nullable=False)
    action = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending | applied | verified | skipped
    audit_snapshot_id = Column(Integer, ForeignKey("audit_snapshots.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cycle = relationship("OptimizationCycle", back_populates="steps")

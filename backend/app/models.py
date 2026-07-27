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
    keywords = relationship("Keyword", back_populates="audit")


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

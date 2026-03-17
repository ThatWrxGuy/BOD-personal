"""
BB-APP-001 Phase 1: Database Schema

PostgreSQL schema for Busy Bee application.
SQLAlchemy models with migrations support.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# ============== User & Identity ==============

class User(Base):
    """User account table."""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    default_horizon: Mapped[str] = mapped_column(String(20), default="weekly")
    notification_preference: Mapped[str] = mapped_column(String(20), default="digest")
    
    # Relationships
    profile: Mapped[Optional["Profile"]] = relationship("Profile", back_populates="user", uselist=False)
    goals: Mapped[list["UserGoal"]] = relationship("UserGoal", back_populates="user")
    signals: Mapped[list["RawSignal"]] = relationship("RawSignal", back_populates="user")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="user")
    actions: Mapped[list["ActionItem"]] = relationship("ActionItem", back_populates="user")
    memories: Mapped[list["MemoryEntry"]] = relationship("MemoryEntry", back_populates="user")
    reviews: Mapped[list["ReviewCycle"]] = relationship("ReviewCycle", back_populates="user")
    briefs: Mapped[list["ExecutiveBriefRecord"]] = relationship("ExecutiveBriefRecord", back_populates="user")
    integrations: Mapped[list["Integration"]] = relationship("Integration", back_populates="user")


class Profile(Base):
    """User profile with life context."""
    __tablename__ = "profiles"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    
    # Life stage
    life_stage: Mapped[str] = mapped_column(String(50), default="early_career")
    
    # Emphasis
    finance_emphasis: Mapped[int] = mapped_column(Integer, default=20)
    health_emphasis: Mapped[int] = mapped_column(Integer, default=20)
    career_emphasis: Mapped[int] = mapped_column(Integer, default=20)
    relationships_emphasis: Mapped[int] = mapped_column(Integer, default=20)
    intelligence_emphasis: Mapped[int] = mapped_column(Integer, default=10)
    life_architecture_emphasis: Mapped[int] = mapped_column(Integer, default=10)
    
    # Operating style
    operating_style: Mapped[str] = mapped_column(String(20), default="balanced")
    planning_horizon_days: Mapped[int] = mapped_column(Integer, default=7)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserGoal(Base):
    """User goals."""
    __tablename__ = "user_goals"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="goals")


# ============== Signals ==============

class RawSignal(Base):
    """Raw signals as received."""
    __tablename__ = "raw_signals"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    signal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="raw")
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="signals")
    normalized: Mapped[Optional["NormalizedSignal"]] = relationship("NormalizedSignal", back_populates="raw_signal", uselist=False)


class NormalizedSignal(Base):
    """Normalized signals after processing."""
    __tablename__ = "normalized_signals"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    raw_signal_id: Mapped[str] = mapped_column(String(36), ForeignKey("raw_signals.id"))
    
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)  # JSON string for complex values
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="normalized")
    source: Mapped[str] = mapped_column(String(20), default="manual")
    
    # Relationships
    raw_signal: Mapped["RawSignal"] = relationship("RawSignal", back_populates="normalized")


class DerivedSignal(Base):
    """Derived signals from analysis."""
    __tablename__ = "derived_signals"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    source_signals: Mapped[str] = mapped_column(JSON, default=list)  # List of signal IDs
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_key: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="percentage")
    algorithm: Mapped[str] = mapped_column(String(50), default="default")
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="derived")


class DomainStateSnapshot(Base):
    """Domain state snapshots."""
    __tablename__ = "domain_state_snapshots"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    trend: Mapped[str] = mapped_column(String(20), default="stable")
    signals_count: Mapped[int] = mapped_column(Integer, default=0)
    active_recommendations: Mapped[int] = mapped_column(Integer, default=0)
    pending_actions: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="healthy")
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_user_domain_snapshot", "user_id", "domain", "snapshot_at"),
    )


# ============== Recommendations ==============

class Recommendation(Base):
    """Recommendations."""
    __tablename__ = "recommendations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(20), default="action")
    urgency: Mapped[int] = mapped_column(Integer, default=3)
    confidence: Mapped[float] = mapped_column(Float, default=0.7)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    explanation: Mapped[Optional["RecommendationExplanation"]] = relationship("RecommendationExplanation", back_populates="recommendation", uselist=False)
    actions: Mapped[list["ActionItem"]] = relationship("ActionItem", back_populates="recommendation")


class RecommendationExplanation(Base):
    """Recommendation explanations."""
    __tablename__ = "recommendation_explanations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    recommendation_id: Mapped[str] = mapped_column(String(36), ForeignKey("recommendations.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    why_generated: Mapped[str] = mapped_column(Text, nullable=False)
    influencing_signals: Mapped[str] = mapped_column(JSON, default=list)
    affected_domains: Mapped[str] = mapped_column(JSON, default=list)
    urgency_rationale: Mapped[str] = mapped_column(Text, default="")
    expected_benefit: Mapped[str] = mapped_column(Text, default="")
    likely_tradeoff: Mapped[str] = mapped_column(Text, default="")
    recommended_time_horizon: Mapped[str] = mapped_column(String(20), default="this_week")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendation: Mapped["Recommendation"] = relationship("Recommendation", back_populates="explanation")


# ============== Actions ==============

class ActionItem(Base):
    """Action items."""
    __tablename__ = "action_items"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    recommendation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("recommendations.id"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="actions")
    recommendation: Mapped[Optional["Recommendation"]] = relationship("Recommendation", back_populates="actions")
    history: Mapped[list["ActionHistory"]] = relationship("ActionHistory", back_populates="action")


class ActionHistory(Base):
    """Action history."""
    __tablename__ = "action_history"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    action_id: Mapped[str] = mapped_column(String(36), ForeignKey("action_items.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    previous_status: Mapped[str] = mapped_column(String(20), nullable=False)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    effectiveness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    outcome_notes: Mapped[str] = mapped_column(Text, default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    action: Mapped["ActionItem"] = relationship("ActionItem", back_populates="history")


# ============== Memory ==============

class MemoryEntry(Base):
    """Memory/note entries."""
    __tablename__ = "memory_entries"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    memory_type: Mapped[str] = mapped_column(String(20), default="note")
    tags: Mapped[str] = mapped_column(JSON, default=list)
    domains: Mapped[str] = mapped_column(JSON, default=list)
    linked_signals: Mapped[str] = mapped_column(JSON, default=list)
    linked_actions: Mapped[str] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memories")


# ============== Reviews ==============

class ReviewCycle(Base):
    """Review cycles."""
    __tablename__ = "review_cycles"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    review_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily, weekly, monthly
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    summary: Mapped[str] = mapped_column(Text, default="")
    progress_highlights: Mapped[str] = mapped_column(JSON, default=list)
    missed_priorities: Mapped[str] = mapped_column(JSON, default=list)
    lessons_learned: Mapped[str] = mapped_column(JSON, default=list)
    next_week_focus: Mapped[str] = mapped_column(JSON, default=list)
    actions_completed: Mapped[int] = mapped_column(Integer, default=0)
    actions_missed: Mapped[int] = mapped_column(Integer, default=0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reviews")


# ============== Executive Briefs ==============

class ExecutiveBriefRecord(Base):
    """Stored executive briefs."""
    __tablename__ = "executive_briefs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    brief_data: Mapped[str] = mapped_column(JSON, nullable=False)
    system_status: Mapped[str] = mapped_column(String(20), default="healthy")
    strategic_posture: Mapped[str] = mapped_column(String(20), default="neutral")
    readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    signals_processed: Mapped[int] = mapped_column(Integer, default=0)
    active_recommendations: Mapped[int] = mapped_column(Integer, default=0)
    risk_alerts: Mapped[int] = mapped_column(Integer, default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="briefs")


# ============== Integrations ==============

class Integration(Base):
    """External integrations."""
    __tablename__ = "integrations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    integration_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[str] = mapped_column(JSON, default=dict)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sync_status: Mapped[str] = mapped_column(String(20), default="idle")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="integrations")


# ============== System Jobs ==============

class SystemJob(Base):
    """Background system jobs."""
    __tablename__ = "system_jobs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    input_data: Mapped[str] = mapped_column(JSON, default=dict)
    output_data: Mapped[str] = mapped_column(JSON, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# ============== Audit Logs ==============

class AuditLog(Base):
    """Audit log entries."""
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    changes: Mapped[str] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_audit_user_entity", "user_id", "entity_type", "entity_id"),
        Index("_audit_timestamp", "timestamp"),
    )

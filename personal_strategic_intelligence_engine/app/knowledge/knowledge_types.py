"""Knowledge graph data types and models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from sqlalchemy import DateTime, String, Text, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class EntityType(str, Enum):
    """Knowledge graph entity types."""
    USER = "user"
    GOAL = "goal"
    PROJECT = "project"
    TASK = "task"
    HABIT = "habit"
    FINANCIAL_ASSET = "financial_asset"
    EXPENSE = "expense"
    INCOME_SOURCE = "income_source"
    HEALTH_METRIC = "health_metric"
    STRATEGIC_PLAN = "strategic_plan"
    STRATEGIC_INSIGHT = "strategic_insight"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    RESOURCE = "resource"
    RELATIONSHIP = "relationship"


class RelationshipType(str, Enum):
    """Knowledge graph relationship types."""
    GOAL_REQUIRES_PROJECT = "goal_requires_project"
    PROJECT_CONTAINS_TASK = "project_contains_task"
    PROJECT_AFFECTS_GOAL = "project_affects_goal"
    WORKLOAD_AFFECTS_HEALTH = "workload_affects_health"
    INCOME_ENABLES_INVESTMENT = "income_enables_investment"
    EXPENSE_REDUCES_LIQUIDITY = "expense_reduces_liquidity"
    SLEEP_INFLUENCES_PRODUCTIVITY = "sleep_influences_productivity"
    RISK_THREATENS_GOAL = "risk_threatens_goal"
    OPPORTUNITY_SUPPORTS_GOAL = "opportunity_supports_goal"
    TASK_SUPPORTS_PROJECT = "task_supports_project"
    HABIT_AFFECTS_HEALTH = "habit_affects_health"
    PLAN_ADDRESSES_RISK = "plan_addresses_risk"
    PLAN_LEADS_TO_GOAL = "plan_leads_to_goal"


class KnowledgeEntity(Base, TimestampMixin):
    """Knowledge graph entity."""

    __tablename__ = "knowledge_entities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Attributes stored as JSON
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Metadata
    domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    # Timestamps
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_entity_type_domain", "entity_type", "domain"),
    )


class KnowledgeRelationship(Base, TimestampMixin):
    """Knowledge graph relationship."""

    __tablename__ = "knowledge_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Attributes
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Metadata
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # detection, review, planning, manual
    
    __table_args__ = (
        Index("idx_relationship_from", "source_entity_id"),
        Index("idx_relationship_to", "target_entity_id"),
        Index("idx_relationship_type", "relationship_type"),
    )


# Domain constants
class KnowledgeDomain:
    """Knowledge domains."""
    FINANCIAL = "financial"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    PROJECTS = "projects"
    STRATEGIC = "strategic"
    SOCIAL = "social"


# Valid entity-to-relationship mapping
VALID_RELATIONSHIPS = {
    EntityType.GOAL: [RelationshipType.GOAL_REQUIRES_PROJECT, RelationshipType.RISK_THREATENS_GOAL],
    EntityType.PROJECT: [RelationshipType.PROJECT_CONTAINS_TASK, RelationshipType.PROJECT_AFFECTS_GOAL],
    EntityType.TASK: [RelationshipType.TASK_SUPPORTS_PROJECT],
    EntityType.HABIT: [RelationshipType.HABIT_AFFECTS_HEALTH],
    EntityType.STRATEGIC_PLAN: [RelationshipType.PLAN_ADDRESSES_RISK, RelationshipType.PLAN_LEADS_TO_GOAL],
    EntityType.RISK: [RelationshipType.RISK_THREATENS_GOAL],
    EntityType.OPPORTUNITY: [RelationshipType.OPPORTUNITY_SUPPORTS_GOAL],
}

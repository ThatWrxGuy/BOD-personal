"""
BB-APP-001: Service Layer Contracts

Per BB-APP-001 Section 6 - Service Layer Hardening.
Each service exposes clean inputs/outputs, avoids UI coupling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ============== Service Result ==============

@dataclass
class ServiceResult:
    """Standard service result."""
    success: bool
    data: Any = None
    error: str | None = None
    
    @classmethod
    def ok(cls, data: Any = None):
        return cls(success=True, data=data)
    
    @classmethod
    def error(cls, error: str):
        return cls(success=False, error=error)


# ============== Input/Output Models ==============

@dataclass
class OnboardingInput:
    email: str = ""
    username: str = ""
    password: str = ""
    life_stage: str = "early_career"
    top_goals: list[str] = field(default_factory=list)
    major_stressors: list[str] = field(default_factory=list)
    finance_rating: int = 5
    health_rating: int = 5
    career_rating: int = 5
    relationships_rating: int = 5
    intelligence_rating: int = 5
    life_architecture_rating: int = 5
    operating_style: str = "balanced"
    planning_horizon_days: int = 7


@dataclass
class UserContextOutput:
    user_id: str = ""
    email: str = ""
    username: str = ""
    profile: dict = field(default_factory=dict)
    goals: list = field(default_factory=list)
    domain_emphasis: dict = field(default_factory=dict)


@dataclass
class SignalInput:
    user_id: str = ""
    source: str = ""
    content: dict = field(default_factory=dict)
    timestamp: datetime | None = None


@dataclass
class NormalizedSignalOutput:
    signal_id: str = ""
    domain: str = ""
    category: str = ""
    value: Any = None
    confidence: float = 1.0


@dataclass
class RecommendationOutput:
    recommendation_id: str = ""
    title: str = ""
    description: str = ""
    domain: str = ""
    urgency: int = 3
    confidence: float = 0.7
    explanation: str = ""
    affected_domains: list = field(default_factory=list)


@dataclass
class BriefOutput:
    brief_id: str = ""
    system_status: str = "healthy"
    strategic_posture: str = "neutral"
    readiness_score: float = 0.0
    domains: dict = field(default_factory=dict)
    recommendations: list = field(default_factory=list)
    risk_alerts: list = field(default_factory=list)


# ============== Service Interfaces ==============

class UserContextService(ABC):
    """Service for user management and context."""
    
    @abstractmethod
    def create_user(self, input_data: OnboardingInput) -> ServiceResult:
        pass
    
    @abstractmethod
    def get_user_context(self, user_id: str) -> ServiceResult:
        pass
    
    @abstractmethod
    def update_profile(self, user_id: str, updates: dict) -> ServiceResult:
        pass
    
    @abstractmethod
    def add_goal(self, user_id: str, goal_data: dict) -> ServiceResult:
        pass
    
    @abstractmethod
    def authenticate(self, email: str, password: str) -> ServiceResult:
        pass


class SignalIngestionService(ABC):
    """Service for signal ingestion."""
    
    @abstractmethod
    def ingest_signal(self, signal_input: SignalInput) -> ServiceResult:
        pass
    
    @abstractmethod
    def get_signals(self, user_id: str, domain: str | None = None) -> ServiceResult:
        pass


class SignalNormalizationService(ABC):
    """Service for signal normalization."""
    
    @abstractmethod
    def normalize_signal(self, raw_signal_id: str) -> ServiceResult:
        pass
    
    @abstractmethod
    def get_normalized_signals(self, user_id: str, domain: str | None = None) -> ServiceResult:
        pass


class StateSnapshotService(ABC):
    """Service for domain state snapshots."""
    
    @abstractmethod
    def get_current_state(self, user_id: str, domain: str) -> ServiceResult:
        pass
    
    @abstractmethod
    def compute_derived_signals(self, user_id: str, domain: str) -> ServiceResult:
        pass


class RecommendationService(ABC):
    """Service for recommendations."""
    
    @abstractmethod
    def generate_recommendations(self, user_id: str, domain: str | None = None) -> ServiceResult:
        pass
    
    @abstractmethod
    def acknowledge_recommendation(self, recommendation_id: str, action: str) -> ServiceResult:
        pass
    
    @abstractmethod
    def get_active_recommendations(self, user_id: str) -> ServiceResult:
        pass


class ExecutiveBriefService(ABC):
    """Service for executive briefs."""
    
    @abstractmethod
    def generate_brief(self, user_id: str) -> ServiceResult:
        pass
    
    @abstractmethod
    def get_latest_brief(self, user_id: str) -> ServiceResult:
        pass


class ActionTrackingService(ABC):
    """Service for action items."""
    
    @abstractmethod
    def get_actions(self, user_id: str, status: str | None = None) -> ServiceResult:
        pass
    
    @abstractmethod
    def complete_action(self, action_id: str, notes: str = "") -> ServiceResult:
        pass
    
    @abstractmethod
    def get_effectiveness(self, user_id: str, days: int = 30) -> ServiceResult:
        pass


class MemoryService(ABC):
    """Service for memory/note storage."""
    
    @abstractmethod
    def add_memory(self, user_id: str, memory_data: dict) -> ServiceResult:
        pass
    
    @abstractmethod
    def search_memories(self, user_id: str, query: str) -> ServiceResult:
        pass


class ReviewService(ABC):
    """Service for review cycles."""
    
    @abstractmethod
    def start_review(self, user_id: str, review_type: str) -> ServiceResult:
        pass
    
    @abstractmethod
    def complete_review(self, review_id: str, data: dict) -> ServiceResult:
        pass


class NotificationService(ABC):
    """Service for notifications."""
    
    @abstractmethod
    def send_notification(self, user_id: str, notification_data: dict) -> ServiceResult:
        pass


class IntegrationService(ABC):
    """Service for external integrations."""
    
    @abstractmethod
    def connect_integration(self, user_id: str, integration_type: str, config: dict) -> ServiceResult:
        pass
    
    @abstractmethod
    def sync_integration(self, integration_id: str) -> ServiceResult:
        pass


__all__ = [
    "ServiceResult",
    "OnboardingInput", "UserContextOutput", "SignalInput", 
    "NormalizedSignalOutput", "RecommendationOutput", "BriefOutput",
    "UserContextService", "SignalIngestionService", "SignalNormalizationService",
    "StateSnapshotService", "RecommendationService", "ExecutiveBriefService",
    "ActionTrackingService", "MemoryService", "ReviewService", 
    "NotificationService", "IntegrationService",
]

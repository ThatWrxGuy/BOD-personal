"""Review Gate - Canonical review/approval interface for decision pipeline.

This module provides the review gate that sits between strategy adjustment output
and execution authorization, ensuring autonomous actions pass through 
executive/governance review before execution.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ReviewDecision(str, Enum):
    """Review decision outcomes."""
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    NEEDS_MORE_ANALYSIS = "needs_more_analysis"


class ReviewPriority(str, Enum):
    """Review priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk levels for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewRequest(BaseModel):
    """Request for review of an action/adjustment."""
    request_id: UUID = Field(default_factory=uuid4)
    adjustment_id: UUID = Field(..., description="ID of adjustment being reviewed")
    adjustment_type: str = Field(..., description="Type of adjustment")
    adjustment_data: Dict[str, Any] = Field(default_factory=dict, description="Adjustment details")
    
    # Risk assessment
    risk_level: RiskLevel = Field(RiskLevel.MEDIUM, description="Assessed risk level")
    impact_scope: str = Field(..., description="Scope of impact")
    reversibility: str = Field("medium", description="How reversible is this action")
    
    # Context
    source: str = Field(..., description="Source requesting review")
    rationale: str = Field(..., description="Rationale for the action")
    
    # Request metadata
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    requested_by: str = Field("autonomy", description="Who requested the review")


class ReviewResult(BaseModel):
    """Result of a review decision."""
    result_id: UUID = Field(default_factory=uuid4)
    request_id: UUID = Field(..., description="ID of review request")
    
    # Decision
    decision: ReviewDecision = Field(..., description="Review decision")
    priority: ReviewPriority = Field(ReviewPriority.MEDIUM, description="Review priority")
    
    # Details
    reviewer: Optional[str] = Field(None, description="Who performed review")
    reason: str = Field(..., description="Reason for decision")
    conditions: Optional[List[str]] = Field(None, description="Conditions for approval")
    
    # Timing
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_final: bool = Field(True, description="Is this a final decision")


class BaseReviewGate(ABC):
    """Abstract base class for review gates.
    
    Review gates sit between strategy adjustment output and execution,
    ensuring all autonomous actions pass through proper review.
    """
    
    def __init__(self):
        self._initialized = False
    
    @property
    @abstractmethod
    def gate_id(self) -> str:
        """Unique gate identifier."""
        pass
    
    @property
    @abstractmethod
    def gate_type(self) -> str:
        """Type of gate (executive, governance, policy, etc.)."""
        pass
    
    async def initialize(self) -> bool:
        """Initialize the review gate."""
        if self._initialized:
            return True
        logger.info(f"Initializing review gate: {self.gate_id}")
        self._initialized = True
        return True
    
    @abstractmethod
    async def submit_for_review(self, request: ReviewRequest) -> ReviewResult:
        """Submit an adjustment for review.
        
        Args:
            request: Review request with adjustment details
            
        Returns:
            Review result with decision
        """
        pass
    
    @abstractmethod
    async def check_approval_required(self, request: ReviewRequest) -> bool:
        """Check if approval is required for this request.
        
        Args:
            request: Review request
            
        Returns:
            True if approval is required
        """
        pass
    
    @abstractmethod
    async def can_auto_approve(self, request: ReviewRequest) -> bool:
        """Check if this request can be auto-approved (low risk).
        
        Args:
            request: Review request
            
        Returns:
            True if can auto-approve
        """
        pass


class ReviewGateManager:
    """Manages review gates and routes requests appropriately."""
    
    def __init__(self):
        self._gates: Dict[str, BaseReviewGate] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all gates."""
        if self._initialized:
            return
        
        # Import and register default gates
        from app.governance.review_gate import ExecutiveReviewGate, PolicyReviewGate
        
        self.register_gate(ExecutiveReviewGate())
        self.register_gate(PolicyReviewGate())
        
        self._initialized = True
    
    def register_gate(self, gate: BaseReviewGate):
        """Register a review gate."""
        self._gates[gate.gate_id] = gate
        logger.info(f"Registered review gate: {gate.gate_id}")
    
    def get_gate(self, gate_id: str) -> Optional[BaseReviewGate]:
        """Get a gate by ID."""
        return self._gates.get(gate_id)
    
    async def submit_for_review(
        self,
        request: ReviewRequest,
        gate_type: Optional[str] = None,
    ) -> ReviewResult:
        """Submit request to appropriate gate.
        
        Args:
            request: Review request
            gate_type: Specific gate type (or auto-select)
            
        Returns:
            Review result
        """
        await self.initialize()
        
        # Determine which gate to use
        if gate_type:
            gate = self._gates.get(gate_type)
            if not gate:
                logger.warning(f"Gate {gate_type} not found, using default")
                gate = self._default_gate(request)
        else:
            gate = self._select_gate(request)
        
        # Check if approval required
        if not await gate.check_approval_required(request):
            return ReviewResult(
                request_id=request.request_id,
                decision=ReviewDecision.APPROVED,
                reason="No approval required - low risk auto-approve",
                reviewer="system",
            )
        
        # Check auto-approve
        if await gate.can_auto_approve(request):
            return ReviewResult(
                request_id=request.request_id,
                decision=ReviewDecision.APPROVED,
                reason="Auto-approved - low risk",
                reviewer="system",
            )
        
        # Submit for review
        return await gate.submit_for_review(request)
    
    def _select_gate(self, request: ReviewRequest) -> BaseReviewGate:
        """Select appropriate gate based on request."""
        # High risk or critical goes to executive
        if request.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return self._gates.get("executive_review_gate", self._gates.get("default"))
        
        # Policy-sensitive goes to governance
        if request.adjustment_type in ["doctrine_change", "policy_update"]:
            return self._gates.get("policy_review_gate", self._gates.get("default"))
        
        # Default to executive gate
        return self._gates.get("executive_review_gate", self._gates.get("default"))
    
    def _default_gate(self, request: ReviewRequest) -> BaseReviewGate:
        """Get default gate."""
        if self._gates:
            return list(self._gates.values())[0]
        raise ValueError("No review gates registered")


# Singleton
_review_gate_manager: Optional[ReviewGateManager] = None


def get_review_gate_manager() -> ReviewGateManager:
    """Get review gate manager singleton."""
    global _review_gate_manager
    if _review_gate_manager is None:
        _review_gate_manager = ReviewGateManager()
    return _review_gate_manager

"""Intervention Policy - Policy controls for the intervention engine."""
from typing import Optional

from app.intervention.intervention_types import InterventionPolicy


# Default policy settings
DEFAULT_POLICY = InterventionPolicy(
    max_interventions_per_day=3,
    cooldown_hours=6,
    confidence_threshold=0.6,
    enable_auto_execution=True,
    emergency_override=False,
    require_approval_for_emergency=True,
)

# Strict policy for testing
STRICT_POLICY = InterventionPolicy(
    max_interventions_per_day=1,
    cooldown_hours=24,
    confidence_threshold=0.8,
    enable_auto_execution=True,
    emergency_override=False,
    require_approval_for_emergency=True,
)

# Lenient policy for high-risk scenarios
LENIENT_POLICY = InterventionPolicy(
    max_interventions_per_day=5,
    cooldown_hours=3,
    confidence_threshold=0.4,
    enable_auto_execution=True,
    emergency_override=True,
    require_approval_for_emergency=False,
)


def get_policy(policy_name: str = "default") -> InterventionPolicy:
    """Get a policy by name."""
    policies = {
        "default": DEFAULT_POLICY,
        "strict": STRICT_POLICY,
        "lenient": LENIENT_POLICY,
    }
    return policies.get(policy_name, DEFAULT_POLICY)


def validate_policy(policy: InterventionPolicy) -> bool:
    """Validate policy settings."""
    
    if policy.max_interventions_per_day < 1:
        return False
    
    if policy.cooldown_hours < 1:
        return False
    
    if not 0 <= policy.confidence_threshold <= 1:
        return False
    
    return True

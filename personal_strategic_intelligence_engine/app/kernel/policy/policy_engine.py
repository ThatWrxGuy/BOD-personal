"""Policy Governance Engine - Enforces strategic constraints."""
import uuid
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.kernel import PolicyRule, PolicyCategory
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class PolicyEngine:
    """Enforces strategic constraints and policies."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings = get_settings()
        self._cached_policies: Optional[List[PolicyRule]] = None
    
    async def initialize_policies(self) -> None:
        """Initialize default policies if none exist."""
        
        result = await self.session.execute(select(PolicyRule))
        existing = list(result.scalars().all())
        
        if not existing:
            # Risk policies
            policies = [
                {
                    "name": "max_capital_at_risk",
                    "category": PolicyCategory.RISK,
                    "type": "limit",
                    "rule": "max_capital_at_risk <= 0.1",
                    "threshold": 0.1,
                    "action": "block",
                    "description": "Maximum 10% of capital at risk",
                },
                {
                    "name": "max_strategy_exposure",
                    "category": PolicyCategory.RISK,
                    "type": "limit",
                    "rule": "max_strategy_exposure <= 0.25",
                    "threshold": 0.25,
                    "action": "block",
                    "description": "Maximum 25% exposure to single strategy",
                },
                {
                    "name": "max_drawdown_tolerance",
                    "category": PolicyCategory.RISK,
                    "type": "threshold",
                    "rule": "current_drawdown <= 0.2",
                    "threshold": 0.2,
                    "action": "alert",
                    "description": "Alert if drawdown exceeds 20%",
                },
                # Execution policies
                {
                    "name": "manual_approval_required",
                    "category": PolicyCategory.EXECUTION,
                    "type": "requirement",
                    "rule": "manual_approval == true",
                    "threshold": 1.0,
                    "action": "enforce",
                    "description": "Manual approval required for all actions",
                },
                {
                    "name": "trade_frequency_limit",
                    "category": PolicyCategory.EXECUTION,
                    "type": "limit",
                    "rule": "daily_trades <= 10",
                    "threshold": 10,
                    "action": "block",
                    "description": "Maximum 10 trades per day",
                },
                # Safety policies
                {
                    "name": "kill_switch_enabled",
                    "category": PolicyCategory.SAFETY,
                    "type": "requirement",
                    "rule": "kill_switch == enabled",
                    "threshold": 1.0,
                    "action": "enforce",
                    "description": "Kill switch must be enabled",
                },
                {
                    "name": "confidence_threshold",
                    "category": PolicyCategory.SAFETY,
                    "type": "threshold",
                    "rule": "decision_confidence >= 0.7",
                    "threshold": 0.7,
                    "action": "block",
                    "description": "Minimum 70% confidence for decisions",
                },
            ]
            
            for p in policies:
                policy = PolicyRule(
                    policy_name=p["name"],
                    policy_category=p["category"],
                    policy_type=p["type"],
                    rule_expression=p["rule"],
                    threshold_value=p["threshold"],
                    enforcement_action=p["action"],
                    description=p["description"],
                )
                self.session.add(policy)
            
            await self.session.commit()
            logger.info("Initialized default policies")
    
    async def evaluate_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a decision against all policies."""
        
        if self._cached_policies is None:
            result = await self.session.execute(
                select(PolicyRule).where(PolicyRule.is_enabled == True)
            )
            self._cached_policies = list(result.scalars().all())
        
        violations = []
        warnings = []
        
        for policy in self._cached_policies:
            result = self._check_policy(policy, decision)
            
            if result["violated"]:
                if policy.enforcement_action == "block":
                    violations.append({
                        "policy": policy.policy_name,
                        "message": f"Policy violation: {policy.description}",
                        "severity": "critical",
                    })
                elif policy.enforcement_action == "alert":
                    warnings.append({
                        "policy": policy.policy_name,
                        "message": policy.description,
                        "severity": "warning",
                    })
        
        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "policies_checked": len(self._cached_policies),
        }
    
    def _check_policy(self, policy: PolicyRule, decision: Dict[str, Any]) -> Dict[str, bool]:
        """Check a single policy against a decision."""
        
        # Simple policy evaluation
        violated = False
        
        if policy.policy_name == "manual_approval_required":
            if not self.settings.manual_approval_required:
                violated = True
        
        elif policy.policy_name == "kill_switch_enabled":
            if not self.settings.enable_kill_switch:
                violated = True
        
        elif policy.policy_name == "max_capital_at_risk":
            capital_at_risk = decision.get("capital_at_risk", 0)
            if capital_at_risk > (policy.threshold_value or 0.1):
                violated = True
        
        elif policy.policy_name == "confidence_threshold":
            confidence = decision.get("confidence", 1.0)
            if confidence < (policy.threshold_value or 0.7):
                violated = True
        
        elif policy.policy_name == "trade_frequency_limit":
            daily_trades = decision.get("daily_trades", 0)
            if daily_trades >= (policy.threshold_value or 10):
                violated = True
        
        return {"violated": violated}
    
    async def get_active_policies(self) -> List[Dict[str, Any]]:
        """Get all active policies."""
        
        if self._cached_policies is None:
            result = await self.session.execute(
                select(PolicyRule).where(PolicyRule.is_enabled == True)
            )
            self._cached_policies = list(result.scalars().all())
        
        return [
            {
                "id": str(p.id),
                "name": p.policy_name,
                "category": p.policy_category,
                "type": p.policy_type,
                "description": p.description,
                "threshold": p.threshold_value,
                "action": p.enforcement_action,
            }
            for p in self._cached_policies
        ]
    
    async def get_policies_by_category(self, category: str) -> List[PolicyRule]:
        """Get policies by category."""
        
        result = await self.session.execute(
            select(PolicyRule).where(
                PolicyRule.policy_category == category,
                PolicyRule.is_enabled == True,
            )
        )
        return list(result.scalars().all())


async def get_policy_engine(session: AsyncSession) -> PolicyEngine:
    """Get policy engine instance."""
    engine = PolicyEngine(session)
    await engine.initialize_policies()
    return engine

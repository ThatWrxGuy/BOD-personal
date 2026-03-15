"""Kernel Controller - Orchestrates the strategic control loop."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.kernel.state_model.state_model_engine import StateModelEngine, get_state_model_engine
from app.kernel.priorities.priority_engine import PriorityEngine, get_priority_engine
from app.kernel.policy.policy_engine import PolicyEngine, get_policy_engine
from app.kernel.decision_utility.decision_utility_engine import DecisionUtilityEngine, get_decision_utility_engine
from app.models.kernel import KernelCycleLog, KernelMode
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class KernelController:
    """Central orchestrator for the strategic control loop."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings = get_settings()
        
        # Initialize subsystems
        self.state_engine: Optional[StateModelEngine] = None
        self.priority_engine: Optional[PriorityEngine] = None
        self.policy_engine: Optional[PolicyEngine] = None
        self.utility_engine: Optional[DecisionUtilityEngine] = None
        
        # Cycle tracking
        self.cycle_number = 0
        self.mode = KernelMode.OBSERVATION
    
    async def initialize(self) -> None:
        """Initialize all kernel subsystems."""
        
        logger.info("Initializing Strategic Kernel...")
        
        self.state_engine = await get_state_model_engine(self.session)
        self.priority_engine = await get_priority_engine(self.session)
        self.policy_engine = await get_policy_engine(self.session)
        self.utility_engine = await get_decision_utility_engine(self.session)
        
        # Update priorities
        await self.priority_engine.update_priorities()
        
        # Capture initial state
        await self.state_engine.capture_snapshot()
        
        logger.info("Strategic Kernel initialized")
    
    async def run_cycle(self) -> Dict[str, Any]:
        """Run one complete strategic control cycle."""
        
        self.cycle_number += 1
        cycle_start = datetime.utcnow()
        
        logger.info(f"Starting kernel cycle {self.cycle_number}")
        
        # Create cycle log
        cycle_log = KernelCycleLog(
            cycle_number=self.cycle_number,
            cycle_mode=self.mode,
            cycle_start=cycle_start,
        )
        self.session.add(cycle_log)
        
        try:
            # Step 1: Observe - Collect signals and update state
            signals_collected = await self._observe()
            cycle_log.signals_collected = signals_collected
            
            # Step 2: Update state model
            state_updates = await self._update_state()
            cycle_log.state_updates = state_updates
            
            # Step 3: Update priorities
            priorities_updated = await self._update_priorities()
            cycle_log.priorities_updated = priorities_updated
            
            # Step 4: Generate and evaluate decision opportunities
            decisions = await self._generate_decisions()
            cycle_log.decisions_evaluated = len(decisions)
            
            # Step 5: Policy evaluation
            evaluated = await self._evaluate_policies(decisions)
            
            # Step 6: Recommend or execute actions
            actions = await self._determine_actions(evaluated)
            cycle_log.actions_recommended = len(actions)
            
            # Step 7: Execute if in autonomous mode
            if self.mode == KernelMode.AUTONOMOUS:
                executed = await self._execute_actions(actions)
                cycle_log.actions_executed = executed
            
            # Step 8: Learn from outcomes (in background)
            await self._learn()
            
            cycle_log.cycle_end = datetime.utcnow()
            cycle_log.cycle_duration_ms = int(
                (cycle_log.cycle_end - cycle_start).total_seconds() * 1000
            )
            
            await self.session.commit()
            
            logger.info(f"Kernel cycle {self.cycle_number} completed in {cycle_log.cycle_duration_ms}ms")
            
            return {
                "cycle_number": self.cycle_number,
                "mode": self.mode,
                "signals_collected": signals_collected,
                "decisions_evaluated": len(decisions),
                "actions_recommended": len(actions),
                "actions_executed": cycle_log.actions_executed,
                "duration_ms": cycle_log.cycle_duration_ms,
            }
            
        except Exception as e:
            logger.error(f"Error in kernel cycle {self.cycle_number}: {e}")
            cycle_log.cycle_end = datetime.utcnow()
            await self.session.commit()
            raise
    
    async def _observe(self) -> int:
        """Observe and collect signals."""
        # In a full implementation, this would pull from signal collectors
        return 0
    
    async def _update_state(self) -> Dict[str, Any]:
        """Update system state model."""
        
        # Refresh state from various sources
        state = await self.state_engine.get_current_state()
        
        # Capture snapshot periodically
        if self.cycle_number % 10 == 0:
            await self.state_engine.capture_snapshot()
        
        return {"updated": True, "domains": list(state.keys())}
    
    async def _update_priorities(self) -> bool:
        """Update strategic priorities based on state."""
        
        priorities = await self.priority_engine.update_priorities()
        
        return True
    
    async def _generate_decisions(self) -> List[Dict[str, Any]]:
        """Generate potential decision opportunities."""
        
        # Get current state and priorities
        state = await self.state_engine.get_current_state()
        priorities = await self.priority_engine.get_active_priorities()
        
        decisions = []
        
        # Generate context-aware decision opportunities
        # In a full implementation, this would be more sophisticated
        
        return decisions
    
    async def _evaluate_policies(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate decisions against policies."""
        
        evaluated = []
        
        for decision in decisions:
            policy_result = await self.policy_engine.evaluate_decision(decision)
            
            evaluated.append({
                "decision": decision,
                "policy_result": policy_result,
                "allowed": policy_result["allowed"],
            })
        
        return evaluated
    
    async def _determine_actions(self, evaluated: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Determine recommended actions based on evaluation."""
        
        actions = []
        
        for item in evaluated:
            if item["allowed"]:
                decision = item["decision"]
                
                # Score the decision
                score = await self.utility_engine.score_decision(
                    decision_type=decision.get("type", "UNKNOWN"),
                    decision_description=decision.get("description", ""),
                    expected_value=decision.get("expected_value", 0.5),
                    risk_assessment=decision.get("risk", 0.5),
                    confidence=decision.get("confidence", 0.5),
                )
                
                actions.append({
                    "decision": decision,
                    "utility_score": score.utility_score,
                    "recommendation": "proceed" if score.utility_score > 0.5 else "defer",
                })
        
        return actions
    
    async def _execute_actions(self, actions: List[Dict[str, Any]]) -> int:
        """Execute approved actions."""
        
        # Only execute in autonomous mode with safety checks
        if self.mode != KernelMode.AUTONOMOUS:
            return 0
        
        if not self.settings.system_execution_enabled:
            logger.warning("Execution attempted but system_execution_enabled is false")
            return 0
        
        executed = 0
        
        for action in actions:
            if action["recommendation"] == "proceed":
                # In a full implementation, dispatch to execution layer
                logger.info(f"Would execute: {action['decision'].get('type')}")
                executed += 1
        
        return executed
    
    async def _learn(self) -> None:
        """Learn from recent outcomes."""
        # In a full implementation, this would update doctrine
        pass
    
    def set_mode(self, mode: str) -> None:
        """Set kernel operation mode."""
        
        if mode.upper() == "OBSERVATION":
            self.mode = KernelMode.OBSERVATION
        elif mode.upper() == "ADVISORY":
            self.mode = KernelMode.ADVISORY
        elif mode.upper() == "AUTONOMOUS":
            self.mode = KernelMode.AUTONOMOUS
        
        logger.info(f"Kernel mode set to: {self.mode}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get kernel status."""
        
        state = await self.state_engine.get_current_state() if self.state_engine else {}
        priorities = await self.priority_engine.get_active_priorities() if self.priority_engine else []
        policies = await self.policy_engine.get_active_policies() if self.policy_engine else []
        
        return {
            "mode": self.mode,
            "cycle_number": self.cycle_number,
            "state_domains": list(state.keys()),
            "active_priorities": len(priorities),
            "active_policies": len(policies),
            "execution_enabled": self.settings.system_execution_enabled,
            "kill_switch_enabled": self.settings.enable_kill_switch,
        }


async def get_kernel_controller(session: AsyncSession) -> KernelController:
    """Get kernel controller instance."""
    controller = KernelController(session)
    await controller.initialize()
    return controller

"""Audit Cycle Runner.

Runs multi-cycle system simulations and captures outputs.
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.strategic_audit.audit_models import (
    CycleAuditRecord,
    DecisionRecord,
    GovernanceOutcome,
    LearningUpdate,
    MemoryRelationship,
    PatternInsight,
    SignalObservation,
    TimeHorizon,
)


class AuditCycleRunner:
    """Runs audit cycles and captures system behavior."""
    
    def __init__(self):
        self._cycles: List[CycleAuditRecord] = []
        self._num_daily: int = 30
    
    def run_simulation(
        self,
        num_daily: int = 30,
        num_weekly: int = 12,
        num_monthly: int = 6,
        num_quarterly: int = 2,
        num_yearly: int = 1,
    ) -> List[CycleAuditRecord]:
        """Run full simulation across all time horizons."""
        
        self._cycles = []
        self._num_daily = num_daily
        
        # Run daily cycles
        for i in range(num_daily):
            cycle = self._run_daily_cycle(i + 1)
            self._cycles.append(cycle)
        
        # Run weekly cycles
        for i in range(num_weekly):
            cycle = self._run_weekly_cycle(i + 1, num_daily)
            self._cycles.append(cycle)
        
        # Run monthly cycles
        for i in range(num_monthly):
            cycle = self._run_monthly_cycle(i + 1, num_daily + num_weekly * 7)
            self._cycles.append(cycle)
        
        # Run quarterly cycles
        for i in range(num_quarterly):
            cycle = self._run_quarterly_cycle(i + 1, num_daily + num_weekly * 7 + num_monthly * 30)
            self._cycles.append(cycle)
        
        # Run yearly cycle
        for i in range(num_yearly):
            cycle = self._run_yearly_cycle(1, num_daily)
            self._cycles.append(cycle)
        
        return self._cycles
    
    def _run_daily_cycle(self, day: int) -> CycleAuditRecord:
        """Run a daily cycle."""
        
        # Generate signals for this day
        signals = self._generate_daily_signals(day)
        
        # Generate decisions
        decisions = self._generate_decisions(signals, TimeHorizon.DAILY, day)
        
        # Apply governance
        governance_outcomes = self._apply_governance(decisions)
        
        return CycleAuditRecord(
            cycle_id=f"daily_{day}",
            cycle_number=day,
            timestamp=datetime.utcnow() - timedelta(days=self._num_daily - day),
            time_horizon=TimeHorizon.DAILY,
            day_number=day,
            signals_observed=signals,
            signals_calibrated=len(signals),
            decisions=decisions,
            governance_outcomes=governance_outcomes,
            learning_updates=self._generate_learning_updates(decisions),
            pattern_insights=self._generate_pattern_insights(),
            memory_relationships=self._generate_memory_relationships(),
        )
    
    def _run_weekly_cycle(self, week: int, start_day: int) -> CycleAuditRecord:
        """Run a weekly cycle."""
        
        signals = self._generate_weekly_signals(week)
        decisions = self._generate_decisions(signals, TimeHorizon.WEEKLY, start_day + week * 7)
        governance_outcomes = self._apply_governance(decisions)
        
        return CycleAuditRecord(
            cycle_id=f"weekly_{week}",
            cycle_number=week,
            timestamp=datetime.utcnow() - timedelta(days=start_day + week * 7),
            time_horizon=TimeHorizon.WEEKLY,
            day_number=start_day + week * 7,
            signals_observed=signals,
            signals_calibrated=len(signals),
            decisions=decisions,
            governance_outcomes=governance_outcomes,
            learning_updates=self._generate_learning_updates(decisions),
            pattern_insights=self._generate_pattern_insights(),
            memory_relationships=self._generate_memory_relationships(),
        )
    
    def _run_monthly_cycle(self, month: int, start_day: int) -> CycleAuditRecord:
        """Run a monthly cycle."""
        
        signals = self._generate_monthly_signals(month)
        decisions = self._generate_decisions(signals, TimeHorizon.MONTHLY, start_day + month * 30)
        governance_outcomes = self._apply_governance(decisions)
        
        return CycleAuditRecord(
            cycle_id=f"monthly_{month}",
            cycle_number=month,
            timestamp=datetime.utcnow() - timedelta(days=start_day + month * 30),
            time_horizon=TimeHorizon.MONTHLY,
            day_number=start_day + month * 30,
            signals_observed=signals,
            signals_calibrated=len(signals),
            decisions=decisions,
            governance_outcomes=governance_outcomes,
            learning_updates=self._generate_learning_updates(decisions),
            pattern_insights=self._generate_pattern_insights(),
            memory_relationships=self._generate_memory_relationships(),
        )
    
    def _run_quarterly_cycle(self, quarter: int, start_day: int) -> CycleAuditRecord:
        """Run a quarterly cycle."""
        
        signals = self._generate_quarterly_signals(quarter)
        decisions = self._generate_decisions(signals, TimeHorizon.QUARTERLY, start_day + quarter * 90)
        governance_outcomes = self._apply_governance(decisions)
        
        return CycleAuditRecord(
            cycle_id=f"quarterly_{quarter}",
            cycle_number=quarter,
            timestamp=datetime.utcnow() - timedelta(days=start_day + quarter * 90),
            time_horizon=TimeHorizon.QUARTERLY,
            day_number=start_day + quarter * 90,
            signals_observed=signals,
            signals_calibrated=len(signals),
            decisions=decisions,
            governance_outcomes=governance_outcomes,
            learning_updates=self._generate_learning_updates(decisions),
            pattern_insights=self._generate_pattern_insights(),
            memory_relationships=self._generate_memory_relationships(),
        )
    
    def _run_yearly_cycle(self, year: int, start_day: int) -> CycleAuditRecord:
        """Run a yearly cycle."""
        
        signals = self._generate_yearly_signals(year)
        decisions = self._generate_decisions(signals, TimeHorizon.YEARLY, start_day + year * 365)
        governance_outcomes = self._apply_governance(decisions)
        
        return CycleAuditRecord(
            cycle_id=f"yearly_{year}",
            cycle_number=year,
            timestamp=datetime.utcnow() - timedelta(days=start_day + year * 365),
            time_horizon=TimeHorizon.YEARLY,
            day_number=start_day + year * 365,
            signals_observed=signals,
            signals_calibrated=len(signals),
            decisions=decisions,
            governance_outcomes=governance_outcomes,
            learning_updates=self._generate_learning_updates(decisions),
            pattern_insights=self._generate_pattern_insights(),
            memory_relationships=self._generate_memory_relationships(),
        )
    
    def _generate_daily_signals(self, day: int) -> List[SignalObservation]:
        """Generate signals for daily cycle."""
        
        signals = []
        
        # Workload signals (varies by day)
        signals.append(SignalObservation(
            signal_id=f"s_calendar_{day}",
            signal_type="meeting_density",
            domain="calendar",
            value=0.4 + random.random() * 0.4,  # 0.4-0.8
            timestamp=datetime.utcnow(),
            calibrated_value=0.5,
            weight=0.8,
            source="calendar_connector",
        ))
        
        # Task signals
        signals.append(SignalObservation(
            signal_id=f"s_tasks_{day}",
            signal_type="task_backlog",
            domain="tasks",
            value=0.3 + random.random() * 0.4,
            timestamp=datetime.utcnow(),
            calibrated_value=0.4,
            weight=0.75,
            source="tasks_connector",
        ))
        
        # Energy signals
        signals.append(SignalObservation(
            signal_id=f"s_health_{day}",
            signal_type="energy_level",
            domain="health",
            value=0.5 + random.random() * 0.3,
            timestamp=datetime.utcnow(),
            calibrated_value=0.6,
            weight=0.9,
            source="health_connector",
        ))
        
        return signals
    
    def _generate_weekly_signals(self, week: int) -> List[SignalObservation]:
        """Generate signals for weekly cycle."""
        
        signals = []
        
        # More significant signals for weekly
        signals.append(SignalObservation(
            signal_id=f"s_weekly_{week}",
            signal_type="schedule_overload",
            domain="calendar",
            value=0.6 + random.random() * 0.3,
            timestamp=datetime.utcnow(),
            calibrated_value=0.7,
            weight=0.85,
            source="calendar_connector",
        ))
        
        signals.append(SignalObservation(
            signal_id=f"s_weekly_tasks_{week}",
            signal_type="completion_rate",
            domain="tasks",
            value=0.5 + random.random() * 0.3,
            timestamp=datetime.utcnow(),
            calibrated_value=0.6,
            weight=0.8,
            source="tasks_connector",
        ))
        
        return signals
    
    def _generate_monthly_signals(self, month: int) -> List[SignalObservation]:
        """Generate signals for monthly cycle."""
        
        signals = []
        
        signals.append(SignalObservation(
            signal_id=f"s_monthly_{month}",
            signal_type="liquidity_change",
            domain="finance",
            value=0.3 + random.random() * 0.4,
            timestamp=datetime.utcnow(),
            calibrated_value=0.5,
            weight=0.9,
            source="finance_connector",
        ))
        
        return signals
    
    def _generate_quarterly_signals(self, quarter: int) -> List[SignalObservation]:
        """Generate signals for quarterly cycle."""
        
        signals = []
        
        signals.append(SignalObservation(
            signal_id=f"s_quarterly_{quarter}",
            signal_type="savings_trend",
            domain="finance",
            value=0.4 + random.random() * 0.3,
            timestamp=datetime.utcnow(),
            calibrated_value=0.55,
            weight=0.9,
            source="finance_connector",
        ))
        
        return signals
    
    def _generate_yearly_signals(self, year: int) -> List[SignalObservation]:
        """Generate signals for yearly cycle."""
        
        signals = []
        
        # Major strategic signals
        signals.append(SignalObservation(
            signal_id=f"s_yearly_{year}",
            signal_type="income_stability",
            domain="finance",
            value=0.7 + random.random() * 0.2,
            timestamp=datetime.utcnow(),
            calibrated_value=0.8,
            weight=0.95,
            source="finance_connector",
        ))
        
        return signals
    
    def _generate_decisions(
        self,
        signals: List[SignalObservation],
        time_horizon: TimeHorizon,
        day: int,
    ) -> List[DecisionRecord]:
        """Generate decisions based on signals."""
        
        decisions = []
        
        # Decision templates by time horizon
        templates = {
            TimeHorizon.DAILY: [
                {"type": "adjust_daily_priorities", "action": "adjust_daily_priorities", "desc": "Adjust today's priorities"},
                {"type": "schedule_recovery", "action": "schedule_recovery", "desc": "Schedule recovery block"},
                {"type": "reduce_meetings", "action": "reduce_meetings", "desc": "Reduce meeting density"},
            ],
            TimeHorizon.WEEKLY: [
                {"type": "rebalance_workload", "action": "reduce_commitments", "desc": "Rebalance workload distribution"},
                {"type": "shift_focus", "action": "prioritize_goals", "desc": "Shift focus to high-impact goals"},
                {"type": "adjust_strategy", "action": "schedule_recovery", "desc": "Adjust weekly strategy"},
            ],
            TimeHorizon.MONTHLY: [
                {"type": "financial_rebalance", "action": "increase_savings", "desc": "Financial rebalancing"},
                {"type": "goal_reprioritization", "action": "prioritize_goals", "desc": "Goal reprioritization"},
            ],
            TimeHorizon.QUARTERLY: [
                {"type": "resource_allocation", "action": "reallocate_resources", "desc": "Resource allocation shift"},
                {"type": "focus_changes", "action": "focus_on_core", "desc": "Focus area changes"},
            ],
            TimeHorizon.YEARLY: [
                {"type": "major_strategy", "action": "major_life_direction", "desc": "Major strategic direction"},
                {"type": "investment_focus", "action": "investment_strategy", "desc": "Investment focus review"},
            ],
        }
        
        # Generate 1-3 decisions based on signals
        num_decisions = random.randint(1, min(3, len(signals) + 1))
        
        for i in range(num_decisions):
            template = random.choice(templates[time_horizon])
            
            decision = DecisionRecord(
                decision_id=f"d_{time_horizon.value}_{day}_{i}",
                timestamp=datetime.utcnow(),
                decision_type=template["type"],
                action_type=template["action"],
                description=template["desc"],
                time_horizon=time_horizon,
                domains=[s.domain for s in signals],
                triggered_by=[s.signal_id for s in signals[:3]],
                confidence=0.6 + random.random() * 0.3,
            )
            
            decisions.append(decision)
        
        return decisions
    
    def _apply_governance(self, decisions: List[DecisionRecord]) -> List[GovernanceOutcome]:
        """Apply governance to decisions."""
        
        outcomes = []
        
        for decision in decisions:
            # Most decisions approved in simulation
            if random.random() < 0.85:
                outcome = GovernanceOutcome(
                    decision_id=decision.decision_id,
                    approved=True,
                    approval_level="auto",
                )
            else:
                outcome = GovernanceOutcome(
                    decision_id=decision.decision_id,
                    approved=False,
                    requires_manual=True,
                    rejection_reason="Policy check failed",
                    approval_level="manager",
                )
            
            outcomes.append(outcome)
        
        return outcomes
    
    def _generate_learning_updates(self, decisions: List[DecisionRecord]) -> List[LearningUpdate]:
        """Generate learning updates from decisions."""
        
        updates = []
        
        for decision in decisions[:2]:  # Top 2 decisions
            update = LearningUpdate(
                timestamp=datetime.utcnow(),
                update_type="confidence_adjustment",
                entity_type="recommendation",
                entity_id=decision.action_type,
                adjustment=random.uniform(-0.05, 0.05),
                new_confidence=decision.confidence,
            )
            updates.append(update)
        
        return updates
    
    def _generate_pattern_insights(self) -> List[PatternInsight]:
        """Generate pattern insights."""
        
        insights = []
        
        # Occasional pattern insights
        if random.random() < 0.3:
            insight = PatternInsight(
                timestamp=datetime.utcnow(),
                insight_type="strategy_effectiveness",
                description="Defensive strategies perform better under workload overload",
                context_cluster="workload_overload",
                strategy_family="defensive_stabilization",
                success_rate=0.78,
                sample_size=15,
            )
            insights.append(insight)
        
        return insights
    
    def _generate_memory_relationships(self) -> List[MemoryRelationship]:
        """Generate memory relationships."""
        
        relationships = []
        
        # Occasional memory relationships
        if random.random() < 0.2:
            rel = MemoryRelationship(
                timestamp=datetime.utcnow(),
                source_node="signal_energy_level",
                target_node="signal_task_backlog",
                relationship_type="contributes_to",
                evidence_count=random.randint(2, 5),
                confidence=0.7,
            )
            relationships.append(rel)
        
        return relationships
    
    def get_cycles(self) -> List[CycleAuditRecord]:
        """Get all recorded cycles."""
        return self._cycles


def create_audit_cycle_runner() -> AuditCycleRunner:
    """Create an audit cycle runner."""
    return AuditCycleRunner()

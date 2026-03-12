"""Life Domain Optimization Engine.

This module provides multi-domain strategic balancing capabilities for the
Personal Strategic Intelligence Engine. It models major life domains, scores
their performance, detects imbalances, evaluates tradeoffs, and recommends
optimization actions.

Core Components:
- Domain Modeler: Constructs structured representations of life domains
- Domain Scorer: Calculates performance scores and health metrics
- Domain Optimizer: Determines resource allocation between domains
- Tradeoff Engine: Evaluates tradeoffs between competing domains
- Optimization Policy: Defines constraints, rules, and safeguards
- Optimization Logger: Records optimization cycles and decisions
"""
from app.optimization.optimization_types import (
    LifeDomain,
    DomainCondition,
    OptimizationAction,
    TradeoffType,
    OptimizationPolicy,
    DomainMetrics,
    DomainConditionResult,
    TradeoffDecision,
    OptimizationActionRecommendation,
    OptimizationCycle,
    OptimizationSummary,
    DomainDataInput,
)
from app.optimization.domain_modeler import (
    DomainModeler,
    get_domain_modeler,
)
from app.optimization.domain_scorer import (
    DomainScorer,
    get_domain_scorer,
)
from app.optimization.domain_optimizer import (
    DomainOptimizer,
    get_domain_optimizer,
)
from app.optimization.tradeoff_engine import (
    TradeoffEngine,
    get_tradeoff_engine,
)
from app.optimization.optimization_policy import (
    OptimizationPolicyEngine,
    get_optimization_policy_engine,
)
from app.optimization.optimization_logger import (
    OptimizationLogger,
    get_optimization_logger,
)

__all__ = [
    # Types
    "LifeDomain",
    "DomainCondition",
    "OptimizationAction",
    "TradeoffType",
    "OptimizationPolicy",
    "DomainMetrics",
    "DomainConditionResult",
    "TradeoffDecision",
    "OptimizationActionRecommendation",
    "OptimizationCycle",
    "OptimizationSummary",
    "DomainDataInput",
    # Core classes
    "DomainModeler",
    "get_domain_modeler",
    "DomainScorer",
    "get_domain_scorer",
    "DomainOptimizer",
    "get_domain_optimizer",
    "TradeoffEngine",
    "get_tradeoff_engine",
    "OptimizationPolicyEngine",
    "get_optimization_policy_engine",
    "OptimizationLogger",
    "get_optimization_logger",
]

"""Domain Source Registry - Pre-configured source bundles for each domain.

This module provides source bundles for:
- Finance
- Health & Nutrition
- Fitness
- Operations
- Strategy/Risk
"""
from app.data_platform.models import SourceRecord, SourceType, TrustTier


# =============================================================================
# FINANCE DOMAIN SOURCES
# =============================================================================
FINANCE_SOURCES = [
    SourceRecord(
        source_id="finance_macro_us",
        source_name="US Macroeconomic Data",
        domain="finance",
        source_type=SourceType.WEB,
        license="public",
        trust_tier=TrustTier.HIGH,
        refresh_interval=3600,
        enabled=True,
        agent_access_tags=["domain:finance", "strategy", "risk"],
    ),
    SourceRecord(
        source_id="finance_macro_global",
        source_name="Global Macroeconomic Data",
        domain="finance",
        source_type=SourceType.WEB,
        license="public",
        trust_tier=TrustTier.HIGH,
        refresh_interval=3600,
        enabled=True,
        agent_access_tags=["domain:finance", "strategy", "risk"],
    ),
    SourceRecord(
        source_id="finance_market_quotes",
        source_name="Market Quote Data",
        domain="finance",
        source_type=SourceType.API,
        license="commercial",
        trust_tier=TrustTier.HIGH,
        refresh_interval=300,
        enabled=True,
        agent_access_tags=["domain:finance", "strategy"],
    ),
    SourceRecord(
        source_id="finance_filings_sec",
        source_name="SEC Filings",
        domain="finance",
        source_type=SourceType.WEB,
        license="public",
        trust_tier=TrustTier.HIGH,
        refresh_interval=86400,
        enabled=True,
        agent_access_tags=["domain:finance", "strategy", "risk"],
    ),
    SourceRecord(
        source_id="finance_research_curated",
        source_name="Curated Financial Research",
        domain="finance",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=86400,
        enabled=True,
        agent_access_tags=["domain:finance", "strategy", "executive"],
    ),
    SourceRecord(
        source_id="finance_news_approved",
        source_name="Approved Financial News Sources",
        domain="finance",
        source_type=SourceType.WEB,
        license="public",
        trust_tier=TrustTier.MEDIUM,
        refresh_interval=1800,
        enabled=True,
        agent_access_tags=["domain:finance", "intelligence"],
    ),
]


# =============================================================================
# HEALTH & NUTRITION DOMAIN SOURCES
# =============================================================================
HEALTH_SOURCES = [
    SourceRecord(
        source_id="health_nutrition_usda",
        source_name="USDA FoodData Central",
        domain="health",
        source_type=SourceType.API,
        license="public",
        trust_tier=TrustTier.HIGH,
        refresh_interval=604800,
        enabled=True,
        agent_access_tags=["domain:health", "domain:fitness"],
    ),
    SourceRecord(
        source_id="health_supplements_db",
        source_name="Supplement Database",
        domain="health",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=2592000,
        enabled=True,
        agent_access_tags=["domain:health"],
    ),
    SourceRecord(
        source_id="health_literature_pubmed",
        source_name="PubMed Health Literature",
        domain="health",
        source_type=SourceType.API,
        license="public",
        trust_tier=TrustTier.HIGH,
        refresh_interval=86400,
        enabled=True,
        agent_access_tags=["domain:health", "intelligence"],
    ),
    SourceRecord(
        source_id="health_wellness_guidance",
        source_name="Evidence-Based Wellness Guidance",
        domain="health",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=2592000,
        enabled=True,
        agent_access_tags=["domain:health", "executive"],
    ),
    SourceRecord(
        source_id="health_nutrition_curated",
        source_name="Curated Nutrition Research",
        domain="health",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=604800,
        enabled=True,
        agent_access_tags=["domain:health", "domain:fitness"],
    ),
]


# =============================================================================
# FITNESS DOMAIN SOURCES
# =============================================================================
FITNESS_SOURCES = [
    SourceRecord(
        source_id="fitness_exercise_lib",
        source_name="Exercise Library",
        domain="fitness",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=2592000,
        enabled=True,
        agent_access_tags=["domain:fitness", "domain:health"],
    ),
    SourceRecord(
        source_id="fitness_templates",
        source_name="Workout Templates",
        domain="fitness",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=604800,
        enabled=True,
        agent_access_tags=["domain:fitness"],
    ),
    SourceRecord(
        source_id="fitness_guidance",
        source_name="Fitness Guidance Documents",
        domain="fitness",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=2592000,
        enabled=True,
        agent_access_tags=["domain:fitness", "domain:health"],
    ),
    SourceRecord(
        source_id="fitness_activity_data",
        source_name="Activity Tracking Data",
        domain="fitness",
        source_type=SourceType.RELATIONAL,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=3600,
        enabled=True,
        agent_access_tags=["domain:fitness"],
    ),
]


# =============================================================================
# OPERATIONS DOMAIN SOURCES
# =============================================================================
OPERATIONS_SOURCES = [
    SourceRecord(
        source_id="ops_sops",
        source_name="Standard Operating Procedures",
        domain="operations",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=2592000,
        enabled=True,
        agent_access_tags=["domain:operations", "executive", "governance"],
    ),
    SourceRecord(
        source_id="ops_procedures",
        source_name="Procedural Documentation",
        domain="operations",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=604800,
        enabled=True,
        agent_access_tags=["domain:operations"],
    ),
    SourceRecord(
        source_id="ops_workflows",
        source_name="Workflow Exports",
        domain="operations",
        source_type=SourceType.RELATIONAL,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=3600,
        enabled=True,
        agent_access_tags=["domain:operations", "domain:strategy"],
    ),
    SourceRecord(
        source_id="ops_tasks",
        source_name="Task Management Data",
        domain="operations",
        source_type=SourceType.RELATIONAL,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=1800,
        enabled=True,
        agent_access_tags=["domain:operations"],
    ),
    SourceRecord(
        source_id="ops_metrics",
        source_name="Operational Metrics",
        domain="operations",
        source_type=SourceType.RELATIONAL,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=900,
        enabled=True,
        agent_access_tags=["domain:operations", "domain:strategy", "executive"],
    ),
]


# =============================================================================
# STRATEGY / RISK DOMAIN SOURCES (Federated)
# =============================================================================
STRATEGY_RISK_SOURCES = [
    SourceRecord(
        source_id="strategy_doctrine",
        source_name="Strategic Doctrine Library",
        domain="strategy",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=2592000,
        enabled=True,
        agent_access_tags=["domain:strategy", "executive", "governance"],
    ),
    SourceRecord(
        source_id="strategy_plans",
        source_name="Strategic Plans Archive",
        domain="strategy",
        source_type=SourceType.RELATIONAL,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=86400,
        enabled=True,
        agent_access_tags=["domain:strategy", "executive"],
    ),
    SourceRecord(
        source_id="risk_register",
        source_name="Risk Register",
        domain="risk",
        source_type=SourceType.RELATIONAL,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=3600,
        enabled=True,
        agent_access_tags=["domain:risk", "executive", "governance"],
    ),
    SourceRecord(
        source_id="risk_assessments",
        source_name="Risk Assessment Reports",
        domain="risk",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=604800,
        enabled=True,
        agent_access_tags=["domain:risk", "executive"],
    ),
    SourceRecord(
        source_id="strategy_intel_synthesis",
        source_name="Intelligence Synthesis Reports",
        domain="strategy",
        source_type=SourceType.DOCUMENT,
        license="internal",
        trust_tier=TrustTier.HIGH,
        refresh_interval=86400,
        enabled=True,
        agent_access_tags=["domain:strategy", "domain:risk", "executive"],
    ),
]


# =============================================================================
# ALL DOMAIN SOURCES
# =============================================================================
ALL_DOMAIN_SOURCES = (
    FINANCE_SOURCES +
    HEALTH_SOURCES +
    FITNESS_SOURCES +
    OPERATIONS_SOURCES +
    STRATEGY_RISK_SOURCES
)


def get_sources_for_domain(domain: str) -> list[SourceRecord]:
    """Get all sources for a specific domain."""
    return [s for s in ALL_DOMAIN_SOURCES if s.domain == domain]


def get_all_domain_sources() -> list[SourceRecord]:
    """Get all domain sources."""
    return list(ALL_DOMAIN_SOURCES)

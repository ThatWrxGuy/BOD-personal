"""Detectors package."""
from app.finance.intelligence.detectors.risk_detector import RiskDetector
from app.finance.intelligence.detectors.opportunity_detector import OpportunityDetector
from app.finance.intelligence.detectors.signal_extractor import SignalExtractor

__all__ = ["RiskDetector", "OpportunityDetector", "SignalExtractor"]

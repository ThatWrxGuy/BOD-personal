"""Signals package for strategic signal ingestion."""
from app.signals.signal_base import (
    SignalData,
    SignalScore,
    BaseSignalCollector,
    BaseSignalProcessor,
    SignalRegistry,
    get_signal_registry,
)
from app.signals.signal_processor import SignalProcessor, get_signal_processor

__all__ = [
    "SignalData",
    "SignalScore",
    "BaseSignalCollector",
    "BaseSignalProcessor",
    "SignalRegistry",
    "get_signal_registry",
    "SignalProcessor",
    "get_signal_processor",
]

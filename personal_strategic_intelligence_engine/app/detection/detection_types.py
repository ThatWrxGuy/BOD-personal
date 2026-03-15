"""Detection data models - Pydantic schemas and enums.

Note: ORM models have been moved to app/models/detection/
This file contains only Pydantic schemas and enums.
"""
from enum import Enum

# Re-export ORM classes for backward compatibility
# TODO: Remove these re-exports and update imports to use app.models.detection
from app.models.detection import DetectedEvent, DetectionEventType, DetectionSeverity, DetectionStatus, DomainType

__all__ = [
    "DetectionEventType",
    "DetectionSeverity", 
    "DetectionStatus",
    "DomainType",
    "DetectedEvent",  # Re-exported from app.models.detection
]

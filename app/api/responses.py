"""
BB-APP-003: Unified API Responses

Standardized API response schemas.
Per BB-APP-003 Section 11 - API Contract Hardening.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar, Optional
from enum import Enum


class ResponseStatus(str, Enum):
    """Response status."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


T = TypeVar('T')


@dataclass
class APIResponse:
    """Base API response."""
    status: ResponseStatus
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SuccessResponse(Generic[T]):
    """Success response with data."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    data: T = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, data: T, message: str = "Success", metadata: dict = None):
        """Create a success response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            metadata=metadata or {},
            message=message,
        )


@dataclass
class ErrorResponse:
    """Error response."""
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: str = ""
    message: str = ""
    retryable: bool = False
    details: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        retryable: bool = False,
        details: dict = None,
    ):
        """Create an error response."""
        return cls(
            status=ResponseStatus.ERROR,
            error_code=error_code,
            message=message,
            retryable=retryable,
            details=details or {},
        )


@dataclass
class PaginatedResponse(Generic[T]):
    """Paginated response."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    data: list[T] = field(default_factory=list)
    pagination: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        data: list[T],
        page: int = 1,
        page_size: int = 20,
        total: int = None,
    ):
        """Create a paginated response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total or len(data),
                "total_pages": (total or len(data)) // page_size + 1,
            },
        )


@dataclass
class CommandResponse:
    """Command execution response."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    success: bool = True
    message: str = ""
    entity_id: Optional[str] = None
    changes: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        success: bool,
        message: str,
        entity_id: str = None,
        changes: dict = None,
    ):
        """Create a command response."""
        return cls(
            status=ResponseStatus.SUCCESS if success else ResponseStatus.ERROR,
            success=success,
            message=message,
            entity_id=entity_id,
            changes=changes or {},
        )


@dataclass
class HealthResponse:
    """Health check response."""
    status: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    checks: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "ResponseStatus",
    "APIResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "CommandResponse",
    "HealthResponse",
]

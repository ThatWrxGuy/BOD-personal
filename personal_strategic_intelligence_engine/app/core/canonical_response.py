"""Canonical Response Models - standardized API response format.

All PSIE API responses follow this canonical structure:

{
    "status": "success | error",
    "data": {},
    "meta": {},
    "timestamp": "ISO8601"
}
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Standard response status."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class ResponseMeta(BaseModel):
    """Metadata for API responses."""
    request_id: Optional[str] = None
    version: str = "1.0.0"
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_count: Optional[int] = None


T = TypeVar('T')


class CanonicalResponse(BaseModel, Generic[T]):
    """Canonical API response format for PSIE.
    
    All endpoints must return responses in this format.
    """
    status: ResponseStatus
    data: T = Field(default_factory=dict)
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @classmethod
    def success(
        cls,
        data: T,
        meta: Optional[ResponseMeta] = None,
    ) -> "CanonicalResponse[T]":
        """Create a success response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            meta=meta or ResponseMeta(),
        )
    
    @classmethod
    def error(
        cls,
        message: str,
        meta: Optional[ResponseMeta] = None,
    ) -> "CanonicalResponse[Dict[str, Any]]":
        """Create an error response."""
        return cls(
            status=ResponseStatus.ERROR,
            data={"message": message},
            meta=meta or ResponseMeta(),
        )
    
    @classmethod
    def pending(
        cls,
        message: str = "Operation in progress",
        meta: Optional[ResponseMeta] = None,
    ) -> "CanonicalResponse[Dict[str, Any]]":
        """Create a pending response."""
        return cls(
            status=ResponseStatus.PENDING,
            data={"message": message},
            meta=meta or ResponseMeta(),
        )


class PaginatedResponse(CanonicalResponse[List[T]]):
    """Paginated response wrapper."""
    
    @classmethod
    def create(
        cls,
        items: List[T],
        page: int = 1,
        page_size: int = 20,
        total_count: Optional[int] = None,
    ) -> "PaginatedResponse[List[T]]":
        """Create a paginated response."""
        if total_count is None:
            total_count = len(items)
        
        meta = ResponseMeta(
            page=page,
            page_size=page_size,
            total_count=total_count,
        )
        
        return cls(
            status=ResponseStatus.SUCCESS,
            data=items,
            meta=meta,
        )


# Utility functions for creating responses
def success_response(data: Any) -> Dict[str, Any]:
    """Create a success response dictionary."""
    return {
        "status": "success",
        "data": data,
        "meta": {"version": "1.0.0"},
        "timestamp": datetime.utcnow().isoformat(),
    }


def error_response(message: str) -> Dict[str, Any]:
    """Create an error response dictionary."""
    return {
        "status": "error",
        "data": {"message": message},
        "meta": {"version": "1.0.0"},
        "timestamp": datetime.utcnow().isoformat(),
    }


def paginated_response(
    items: List[Any],
    page: int = 1,
    page_size: int = 20,
    total: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a paginated response dictionary."""
    return {
        "status": "success",
        "data": items,
        "meta": {
            "version": "1.0.0",
            "page": page,
            "page_size": page_size,
            "total_count": total or len(items),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

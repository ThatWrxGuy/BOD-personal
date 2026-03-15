"""Response Wrapper - provides canonical response format for PSIE endpoints.

This module wraps existing responses in the canonical format:
{
    "status": "success | error",
    "data": {},
    "meta": {},
    "timestamp": "ISO8601"
}
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


def wrap_response(
    data: Any,
    meta: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Wrap any data in canonical response format.
    
    Args:
        data: The response data
        meta: Optional metadata
        request_id: Optional request ID
        
    Returns:
        Canonical response dictionary
    """
    return {
        "status": "success",
        "data": data,
        "meta": meta or {},
        "timestamp": datetime.utcnow().isoformat(),
    }


def wrap_list_response(
    items: List[Any],
    page: int = 1,
    page_size: int = 20,
    total: Optional[int] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Wrap a list response with pagination.
    
    Args:
        items: List of items
        page: Current page number
        page_size: Items per page
        total: Total count (defaults to len(items))
        request_id: Optional request ID
        
    Returns:
        Paginated canonical response
    """
    return {
        "status": "success",
        "data": items,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total_count": total if total is not None else len(items),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def error_response(
    message: str,
    code: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an error response.
    
    Args:
        message: Error message
        code: Optional error code
        request_id: Optional request ID
        
    Returns:
        Error canonical response
    """
    data = {"message": message}
    if code:
        data["code"] = code
    
    return {
        "status": "error",
        "data": data,
        "meta": {},
        "timestamp": datetime.utcnow().isoformat(),
    }


def success_response(
    data: Any,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a success response.
    
    Args:
        data: Response data
        meta: Optional metadata
        
    Returns:
        Success canonical response
    """
    return {
        "status": "success",
        "data": data,
        "meta": meta or {},
        "timestamp": datetime.utcnow().isoformat(),
    }


def pending_response(
    message: str = "Operation in progress",
) -> Dict[str, Any]:
    """Create a pending response.
    
    Args:
        message: Pending message
        
    Returns:
        Pending canonical response
    """
    return {
        "status": "pending",
        "data": {"message": message},
        "meta": {},
        "timestamp": datetime.utcnow().isoformat(),
    }

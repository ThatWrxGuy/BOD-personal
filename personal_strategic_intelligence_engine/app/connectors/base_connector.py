"""Base Connector - Abstract base class for domain connectors.

All domain connectors should inherit from this base class.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base class for data connectors.
    
    All domain connectors must implement:
    - connect(): Initialize connection to data source
    - disconnect(): Clean up connection
    - fetch(): Fetch data from source
    - normalize(): Convert raw data to canonical format
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize connector with configuration.
        
        Args:
            config: Connector-specific configuration
        """
        self.config = config or {}
        self._connected = False
        self._last_fetch: Optional[datetime] = None
    
    @property
    @abstractmethod
    def source_id(self) -> str:
        """Return the source ID for this connector."""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if connector is connected."""
        return self._connected
    
    async def connect(self) -> bool:
        """Establish connection to the data source.
        
        Returns:
            True if connection successful
        """
        logger.info(f"Connecting to source: {self.source_id}")
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from the data source."""
        logger.info(f"Disconnecting from source: {self.source_id}")
        self._connected = False
    
    @abstractmethod
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch raw data from the source.
        
        Args:
            **kwargs: Connector-specific fetch parameters
            
        Returns:
            List of raw data records
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw data to canonical format.
        
        Args:
            raw_data: Raw data from source
            
        Returns:
            Normalized data dictionary
        """
        pass
    
    async def fetch_and_normalize(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch and normalize data in one call.
        
        Args:
            **kwargs: Fetch parameters
            
        Returns:
            List of normalized records
        """
        if not self._connected:
            await self.connect()
        
        raw_data = await self.fetch(**kwargs)
        
        normalized = []
        for record in raw_data:
            try:
                normalized_record = self.normalize(record)
                normalized.append(normalized_record)
            except Exception as e:
                logger.warning(f"Failed to normalize record: {e}")
                continue
        
        self._last_fetch = datetime.utcnow()
        return normalized
    
    async def health_check(self) -> Dict[str, Any]:
        """Check connector health.
        
        Returns:
            Health status dictionary
        """
        return {
            "source_id": self.source_id,
            "connected": self._connected,
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
            "status": "healthy" if self._connected else "disconnected",
        }

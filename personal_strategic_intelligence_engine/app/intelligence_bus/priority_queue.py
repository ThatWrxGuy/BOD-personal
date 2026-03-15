"""Priority Queue for the Strategic Intelligence Bus.

Manages signal processing by urgency.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
import heapq

from app.intelligence_bus.signal_models import Signal, SignalPriority


@dataclass
class PrioritySignal:
    """Signal with priority for queue."""
    priority_value: int
    timestamp: datetime
    signal: Signal
    
    def __lt__(self, other):
        if self.priority_value != other.priority_value:
            return self.priority_value < other.priority_value
        return self.timestamp < other.timestamp


class PriorityQueue:
    """Priority queue for signal processing."""
    
    def __init__(self):
        self._queue: List[PrioritySignal] = []
        self._priority_map = {
            SignalPriority.CRITICAL: 0,
            SignalPriority.HIGH: 1,
            SignalPriority.MEDIUM: 2,
            SignalPriority.LOW: 3,
            SignalPriority.BACKGROUND: 4,
        }
    
    def enqueue(self, signal: Signal) -> None:
        """Add a signal to the queue."""
        
        priority_value = self._priority_map.get(signal.priority, 2)
        
        priority_signal = PrioritySignal(
            priority_value=priority_value,
            timestamp=signal.timestamp,
            signal=signal,
        )
        
        heapq.heappush(self._queue, priority_signal)
    
    def dequeue(self) -> Optional[Signal]:
        """Remove and return the highest priority signal."""
        
        if not self._queue:
            return None
        
        priority_signal = heapq.heappop(self._queue)
        return priority_signal.signal
    
    def peek(self) -> Optional[Signal]:
        """View the highest priority signal without removing."""
        
        if not self._queue:
            return None
        
        return self._queue[0].signal
    
    def size(self) -> int:
        """Get queue size."""
        
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        
        return len(self._queue) == 0
    
    def get_by_priority(self, priority: SignalPriority) -> List[Signal]:
        """Get all signals of a specific priority."""
        
        priority_value = self._priority_map.get(priority, 2)
        
        return [
            ps.signal for ps in self._queue
            if ps.priority_value == priority_value
        ]
    
    def get_pending_count(self) -> Dict[str, int]:
        """Get count of pending signals by priority."""
        
        counts = {p.value: 0 for p in SignalPriority}
        
        for ps in self._queue:
            counts[ps.signal.priority.value] += 1
        
        return counts
    
    def clear(self) -> None:
        """Clear the queue."""
        
        self._queue.clear()


# Global queue
_queue = None

def get_queue() -> PriorityQueue:
    """Get global priority queue."""
    global _queue
    if _queue is None:
        _queue = PriorityQueue()
    return _queue

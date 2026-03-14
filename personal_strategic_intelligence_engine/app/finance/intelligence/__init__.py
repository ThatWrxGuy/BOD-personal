"""Finance Intelligence subsystem package.

This package implements the Finance Intelligence Layer (V19-002).
"""

from app.finance.intelligence import models
from app.finance.intelligence import detectors
from app.finance.intelligence import engines
from app.finance.intelligence import services
from app.finance.intelligence import api

__all__ = ["models", "detectors", "engines", "services", "api"]

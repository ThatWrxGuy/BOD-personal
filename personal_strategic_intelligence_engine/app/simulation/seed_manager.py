"""Seed Manager - Handles deterministic seed normalization and reproducibility."""
import hashlib
import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)


class SeedManager:
    """Manages deterministic seed generation and random state."""
    
    def __init__(self, seed: str):
        self.original_seed = seed
        self._random_generator = self._create_deterministic_generator(seed)
    
    def _create_deterministic_generator(self, seed: str) -> random.Random:
        """Create a deterministic random generator from seed."""
        # Convert seed to a deterministic integer
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        seed_int = int(seed_hash[:16], 16) % (2**31)
        
        # Create generator with this seed
        rng = random.Random(seed_int)
        
        logger.info(f"Initialized deterministic seed: {seed[:20]}... -> {seed_int}")
        
        return rng
    
    @property
    def random(self) -> random.Random:
        """Get the random generator."""
        return self._random_generator
    
    def get_seed_hash(self) -> str:
        """Get the hash of the seed for reproducibility verification."""
        return hashlib.sha256(self.original_seed.encode()).hexdigest()
    
    def reset(self) -> None:
        """Reset the random generator to initial state."""
        self._random_generator = self._create_deterministic_generator(self.original_seed)
    
    def generate_seed_value(self, min_val: int = 0, max_val: int = 100) -> int:
        """Generate a deterministic integer in range."""
        return self._random_generator.randint(min_val, max_val)
    
    def generate_float(self) -> float:
        """Generate a deterministic float between 0 and 1."""
        return self._random_generator.random()
    
    def generate_choice(self, choices: list) -> any:
        """Choose randomly from a list deterministically."""
        return self._random_generator.choice(choices)
    
    def generate_weighted_choice(self, choices: list, weights: list) -> any:
        """Choose from choices with given weights deterministically."""
        return self._random_generator.choices(choices, weights=weights, k=1)[0]
    
    def shuffle(self, items: list) -> list:
        """Shuffle a list deterministically."""
        items_copy = items.copy()
        self._random_generator.shuffle(items_copy)
        return items_copy
    
    def generate_string(self, length: int = 10) -> str:
        """Generate a random string."""
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(self._random_generator.choice(chars) for _ in range(length))
    
    def generate_uuid(self) -> str:
        """Generate a deterministic UUID based on seed."""
        # Use seed to generate consistent UUID
        hash_val = hashlib.md5(self.original_seed.encode()).hexdigest()
        return f"{hash_val[:8]}-{hash_val[8:12]}-{hash_val[12:16]}-{hash_val[16:20]}-{hash_val[20:32]}"
    
    def generate_normal_distributed(self, mean: float = 0.0, std_dev: float = 1.0) -> float:
        """Generate a number from normal distribution."""
        return self._random_generator.gauss(mean, std_dev)
    
    def get_state(self) -> tuple:
        """Get current random state for debugging."""
        return self._random_generator.getstate()
    
    def set_state(self, state: tuple) -> None:
        """Set random state."""
        self._random_generator.setstate(state)


def normalize_seed(seed: str) -> str:
    """Normalize a seed string to a standard format."""
    if not seed:
        raise ValueError("Seed cannot be empty")
    
    # Trim whitespace
    seed = seed.strip()
    
    # Convert to uppercase for consistency
    seed = seed.upper()
    
    # Replace spaces with hyphens
    seed = seed.replace(" ", "-")
    
    return seed


def create_seed_manager(seed: str) -> SeedManager:
    """Create a seed manager from a seed string."""
    normalized = normalize_seed(seed)
    return SeedManager(normalized)


# Global seed managers cache
_seed_managers: dict[str, SeedManager] = {}


def get_seed_manager(seed: str) -> SeedManager:
    """Get or create a seed manager."""
    normalized = normalize_seed(seed)
    
    if normalized not in _seed_managers:
        _seed_managers[normalized] = SeedManager(normalized)
    
    return _seed_managers[normalized]

"""
Dataset adapters for NL2SQL generation.
Each adapter provides dataset-specific prompt building and question loading.
"""

from .base import BaseAdapter
from .ecommerce_bird_sample200 import EcommerceBirdAdapter

ADAPTERS = {
    "ecommerce_bird_sample200": EcommerceBirdAdapter,
}


def get_adapter(name: str) -> BaseAdapter:
    """Get adapter by name."""
    if name not in ADAPTERS:
        raise ValueError(f"Unknown adapter: {name}. Available: {list(ADAPTERS.keys())}")
    return ADAPTERS[name]()

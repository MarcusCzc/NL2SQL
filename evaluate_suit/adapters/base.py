"""
Base adapter interface for dataset-specific NL2SQL prompt construction.
Subclass and implement load_questions() and build_prompt() for each dataset.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BaseAdapter(ABC):
    """Abstract base for dataset adapters. Prompt format and question loading vary by dataset."""

    @abstractmethod
    def load_questions(self, gold_dir: Path) -> List[Dict[str, Any]]:
        """Load questions from dataset gold directory. Return list of question dicts with instance_id."""
        pass

    @abstractmethod
    def build_prompt(self, q: Dict[str, Any], data_dir: Path) -> str:
        """Build LLM prompt for a single question. Schema, hints, format are dataset-specific."""
        pass

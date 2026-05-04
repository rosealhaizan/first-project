"""
storage.py — JSON-based persistence

Tasks are saved to a single JSON file (~/.taskflow/tasks.json).
The storage layer is intentionally separate from the heap so the
two concerns — ordering logic and I/O — stay independent.
"""

import json
import os
from pathlib import Path
from typing import List

from task_manager.task import Task

DEFAULT_PATH = Path.home() / ".taskflow" / "tasks.json"


class Storage:
    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, tasks: List[Task]) -> None:
        """Serialise task list to disk."""
        with open(self.path, "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)

    def load(self) -> List[Task]:
        """Deserialise tasks from disk; returns [] if file absent."""
        if not self.path.exists():
            return []
        with open(self.path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []
        return [Task.from_dict(d) for d in data]

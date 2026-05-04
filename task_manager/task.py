"""
task.py — Task data model

A Task holds all metadata for a single to-do item.
Priority is stored as 1 (highest) – 5 (lowest) so the
min-heap naturally surfaces the most urgent work first.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
import uuid


@dataclass
class Task:
    title: str
    priority: int                          # 1 = critical, 5 = someday
    due_date: Optional[date] = None
    notes: str = ""
    completed: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    # ------------------------------------------------------------------ #
    #  Comparison operators — used by MinHeap to order tasks              #
    #  Primary key : priority (lower number = higher urgency)             #
    #  Tiebreaker  : due_date (earlier date wins; None sorts to the end)  #
    # ------------------------------------------------------------------ #

    def _sort_key(self) -> tuple:
        due = self.due_date or date(9999, 12, 31)   # None → far future
        return (self.priority, due)

    def __lt__(self, other: Task) -> bool:
        return self._sort_key() < other._sort_key()

    def __le__(self, other: Task) -> bool:
        return self._sort_key() <= other._sort_key()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id

    # ------------------------------------------------------------------ #
    #  Serialisation helpers                                               #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "title":      self.title,
            "priority":   self.priority,
            "due_date":   self.due_date.isoformat() if self.due_date else None,
            "notes":      self.notes,
            "completed":  self.completed,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(d: dict) -> Task:
        return Task(
            id=d["id"],
            title=d["title"],
            priority=d["priority"],
            due_date=date.fromisoformat(d["due_date"]) if d.get("due_date") else None,
            notes=d.get("notes", ""),
            completed=d.get("completed", False),
            created_at=d.get("created_at", ""),
        )

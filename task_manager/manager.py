"""
manager.py — TaskManager

This is the bridge between the CLI and the underlying data structures.
All heap operations live here; the CLI layer never touches the heap directly.
"""

from __future__ import annotations
from datetime import date, timedelta
from typing import List, Optional

from task_manager.heap import MinHeap
from task_manager.storage import Storage
from task_manager.task import Task


class TaskManager:
    def __init__(self, storage: Optional[Storage] = None) -> None:
        self._storage = storage or Storage()
        self._heap: MinHeap[Task] = MinHeap()
        self._load()

    # ------------------------------------------------------------------ #
    #  CRUD operations                                                     #
    # ------------------------------------------------------------------ #

    def add(
        self,
        title: str,
        priority: int = 3,
        due_date: Optional[date] = None,
        notes: str = "",
    ) -> Task:
        """Create a task, push it onto the heap, and persist."""
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 (highest) and 5 (lowest).")
        task = Task(title=title, priority=priority, due_date=due_date, notes=notes)
        self._heap.push(task)
        self._save()
        return task

    def complete(self, task_id: str) -> Task:
        """Mark a task as done and remove it from the active heap."""
        task = self._remove_by_id(task_id)
        if task is None:
            raise KeyError(f"No task with id '{task_id}'.")
        task.completed = True
        self._save()
        return task

    def delete(self, task_id: str) -> Task:
        """Permanently remove a task."""
        task = self._remove_by_id(task_id)
        if task is None:
            raise KeyError(f"No task with id '{task_id}'.")
        self._save()
        return task

    def snooze(self, task_id: str, days: int = 1) -> Task:
        """Push a task's due date forward and re-insert into the heap."""
        task = self._remove_by_id(task_id)
        if task is None:
            raise KeyError(f"No task with id '{task_id}'.")
        base = task.due_date or date.today()
        task.due_date = base + timedelta(days=days)
        self._heap.push(task)
        self._save()
        return task

    def update_priority(self, task_id: str, priority: int) -> Task:
        """Change a task's priority and re-insert so heap order is correct."""
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5.")
        task = self._remove_by_id(task_id)
        if task is None:
            raise KeyError(f"No task with id '{task_id}'.")
        task.priority = priority
        self._heap.push(task)
        self._save()
        return task

    # ------------------------------------------------------------------ #
    #  Queries                                                             #
    # ------------------------------------------------------------------ #

    def list_tasks(self) -> List[Task]:
        """Return all active tasks ordered by priority then due date."""
        return self._heap.to_sorted_list()

    def peek_next(self) -> Optional[Task]:
        """Return the single highest-priority task without removing it."""
        return self._heap.peek() if self._heap else None

    def overdue(self) -> List[Task]:
        """Return tasks whose due date has passed."""
        today = date.today()
        return [
            t for t in self.list_tasks()
            if t.due_date and t.due_date < today
        ]

    def stats(self) -> dict:
        tasks = self.list_tasks()
        overdue = self.overdue()
        by_priority = {}
        for p in range(1, 6):
            by_priority[p] = sum(1 for t in tasks if t.priority == p)
        return {
            "total":    len(tasks),
            "overdue":  len(overdue),
            "by_priority": by_priority,
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _remove_by_id(self, task_id: str) -> Optional[Task]:
        return self._heap.remove_by(lambda t: t.id == task_id)

    def _save(self) -> None:
        self._storage.save(self._heap.to_sorted_list())

    def _load(self) -> None:
        tasks = self._storage.load()
        self._heap.heapify(tasks)

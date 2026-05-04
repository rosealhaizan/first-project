"""
tests/test_heap.py — Unit tests for MinHeap and TaskManager
"""

import pytest
from datetime import date, timedelta

from task_manager.heap import MinHeap
from task_manager.task import Task
from task_manager.manager import TaskManager
from task_manager.storage import Storage
from pathlib import Path
import tempfile


# ─── MinHeap tests ────────────────────────────────────────────────────────────

class TestMinHeap:

    def test_push_pop_order(self):
        h = MinHeap()
        for v in [3, 1, 4, 1, 5, 9, 2]:
            h.push(v)
        result = [h.pop() for _ in range(len(h))]
        assert result == sorted([3, 1, 4, 1, 5, 9, 2])

    def test_peek_does_not_remove(self):
        h = MinHeap()
        h.push(7)
        h.push(2)
        assert h.peek() == 2
        assert len(h) == 2

    def test_heapify(self):
        items = [5, 3, 8, 1, 2]
        h = MinHeap()
        h.heapify(items)
        assert h.pop() == 1
        assert h.pop() == 2

    def test_pop_empty_raises(self):
        with pytest.raises(IndexError):
            MinHeap().pop()

    def test_remove_by(self):
        h = MinHeap()
        for v in [4, 2, 6]:
            h.push(v)
        removed = h.remove_by(lambda x: x == 2)
        assert removed == 2
        assert len(h) == 2

    def test_to_sorted_list_is_nondestructive(self):
        h = MinHeap()
        h.heapify([3, 1, 2])
        sorted_list = h.to_sorted_list()
        assert sorted_list == [1, 2, 3]
        assert len(h) == 3  # original heap untouched


# ─── Task comparison tests ────────────────────────────────────────────────────

class TestTaskOrdering:

    def test_lower_priority_number_wins(self):
        t1 = Task("Critical", priority=1)
        t2 = Task("Normal",   priority=3)
        assert t1 < t2

    def test_tiebreak_by_due_date(self):
        today    = date.today()
        tomorrow = today + timedelta(days=1)
        t1 = Task("Earlier", priority=2, due_date=today)
        t2 = Task("Later",   priority=2, due_date=tomorrow)
        assert t1 < t2

    def test_none_due_date_sorts_last(self):
        today = date.today()
        t1 = Task("Has date",  priority=2, due_date=today)
        t2 = Task("No date",   priority=2, due_date=None)
        assert t1 < t2


# ─── TaskManager integration tests ───────────────────────────────────────────

@pytest.fixture
def mgr(tmp_path):
    """TaskManager backed by a temporary storage file."""
    storage = Storage(path=tmp_path / "tasks.json")
    return TaskManager(storage=storage)


class TestTaskManager:

    def test_add_and_list(self, mgr):
        mgr.add("Task A", priority=3)
        mgr.add("Task B", priority=1)
        tasks = mgr.list_tasks()
        assert len(tasks) == 2
        assert tasks[0].priority == 1   # highest priority first

    def test_peek_next(self, mgr):
        mgr.add("Low",  priority=5)
        mgr.add("High", priority=1)
        assert mgr.peek_next().title == "High"

    def test_complete_removes_task(self, mgr):
        task = mgr.add("Finish it", priority=2)
        done = mgr.complete(task.id)
        assert done.completed is True
        assert len(mgr.list_tasks()) == 0

    def test_delete(self, mgr):
        task = mgr.add("Delete me", priority=3)
        mgr.delete(task.id)
        assert len(mgr.list_tasks()) == 0

    def test_snooze_extends_due_date(self, mgr):
        today = date.today()
        task = mgr.add("Snooze me", priority=2, due_date=today)
        snoozed = mgr.snooze(task.id, days=3)
        assert snoozed.due_date == today + timedelta(days=3)

    def test_update_priority_reorders(self, mgr):
        t1 = mgr.add("First",  priority=1)
        t2 = mgr.add("Second", priority=2)
        mgr.update_priority(t1.id, priority=5)
        tasks = mgr.list_tasks()
        assert tasks[0].id == t2.id   # t2 now has highest priority

    def test_overdue(self, mgr):
        past   = date.today() - timedelta(days=3)
        future = date.today() + timedelta(days=3)
        mgr.add("Past due",   priority=2, due_date=past)
        mgr.add("Not due yet", priority=2, due_date=future)
        assert len(mgr.overdue()) == 1

    def test_invalid_priority_raises(self, mgr):
        with pytest.raises(ValueError):
            mgr.add("Bad priority", priority=0)

    def test_complete_unknown_id_raises(self, mgr):
        with pytest.raises(KeyError):
            mgr.complete("nonexistent")

    def test_persistence(self, tmp_path):
        """Data should survive across TaskManager instances."""
        storage = Storage(path=tmp_path / "tasks.json")
        m1 = TaskManager(storage=storage)
        m1.add("Persist me", priority=2)

        m2 = TaskManager(storage=storage)
        assert len(m2.list_tasks()) == 1
        assert m2.list_tasks()[0].title == "Persist me"

    def test_stats(self, mgr):
        mgr.add("A", priority=1)
        mgr.add("B", priority=1)
        mgr.add("C", priority=3)
        s = mgr.stats()
        assert s["total"] == 3
        assert s["by_priority"][1] == 2
        assert s["by_priority"][3] == 1

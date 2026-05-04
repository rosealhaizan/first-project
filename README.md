# TaskFlow 🗂️

A priority-scheduled command-line task manager written in pure Python.

Tasks are stored in a **min-heap** so the most urgent item is always
retrieved in O(1) time, insertions run in O(log n), and the full
sorted list is produced in O(n log n) — no external libraries required.

---

## Features

| Command | What it does |
|---------|-------------|
| `add`   | Create a task with a title, priority (1–5), and optional due date |
| `list`  | Display all tasks ordered by priority then due date |
| `next`  | Peek at the single highest-priority task |
| `complete` | Mark a task done and remove it from the queue |
| `snooze`   | Push a task's due date forward by N days |
| `delete`   | Permanently remove a task |
| `stats`    | Summary report with overdue count and priority breakdown |

---

## Data structures used

```
MinHeap (task_manager/heap.py)
├── push       — O(log n)   sift-up
├── pop        — O(log n)   sift-down
├── peek       — O(1)
├── heapify    — O(n)       bottom-up construction
└── remove_by  — O(n)       linear scan + local heap repair
```

Tasks implement `__lt__` with a two-key comparator:
1. **Priority** (1 = critical, 5 = someday)
2. **Due date** as a tiebreaker (earlier wins; `None` sorts to the end)

---

## Installation

```bash
git clone https://github.com/your-username/taskflow.git
cd taskflow
pip install -r requirements.txt   # only pytest; no runtime deps
```

---

## Usage

```bash
# Add tasks
python main.py add "Submit CS homework" --priority 1 --due 2025-05-10
python main.py add "Read chapter 7"     --priority 3
python main.py add "Clean desk"         --priority 5

# See what's pending
python main.py list

# What should I do right now?
python main.py next

# Done with something
python main.py complete a3f2c1b0

# Need more time
python main.py snooze a3f2c1b0 --days 2

# Dashboard
python main.py stats
```

Sample `list` output:

```
──────────────────────────────────────────────────
  📋  TaskFlow  (3 tasks)
──────────────────────────────────────────────────
 1. Submit CS homework
      id=a3f2c1b0  priority=❗ Critical  due=OVERDUE (May 10)
 2. Read chapter 7
      id=c7d1e2f3  priority=🟡 Normal    due=no due date
 3. Clean desk
      id=b8a9f0e1  priority=⬜ Someday   due=no due date
──────────────────────────────────────────────────
```

---

## Running tests

```bash
pytest tests/ -v
```

All 15 tests cover: heap correctness, task ordering, CRUD operations,
edge cases (invalid priority, unknown ID), and JSON persistence.

---

## Project structure

```
taskflow/
├── main.py                  # CLI entry point (argparse)
├── requirements.txt
├── task_manager/
│   ├── __init__.py
│   ├── heap.py              # MinHeap — from scratch, no heapq
│   ├── task.py              # Task dataclass with comparison operators
│   ├── manager.py           # Business logic layer
│   └── storage.py           # JSON persistence (~/.taskflow/tasks.json)
└── tests/
    └── test_heap.py         # Unit + integration tests (pytest)
```

---

## Design decisions

- **No `heapq` module** — the heap is implemented from scratch to demonstrate the algorithm clearly.
- **Separation of concerns** — heap logic, business rules, and I/O are in separate files.
- **Generic heap** — `MinHeap[T]` works with any type that defines `__lt__`, not just tasks.
- **Pure stdlib** — zero runtime dependencies; only `pytest` is needed for tests.

---



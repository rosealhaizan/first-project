#!/usr/bin/env python3
"""
main.py — TaskFlow CLI

Usage examples
--------------
  python main.py add "Finish DS homework" --priority 1 --due 2025-05-10
  python main.py list
  python main.py next
  python main.py complete a3f2c1b0
  python main.py snooze  a3f2c1b0 --days 2
  python main.py delete  a3f2c1b0
  python main.py stats
"""

import argparse
import sys
from datetime import date

from task_manager.manager import TaskManager

# ── Colour helpers (no third-party deps) ──────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
DIM    = "\033[2m"

PRIORITY_COLORS = {1: RED, 2: YELLOW, 3: CYAN, 4: GREEN, 5: DIM}
PRIORITY_LABELS = {1: "❗ Critical", 2: "🔴 High", 3: "🟡 Normal", 4: "🟢 Low", 5: "⬜ Someday"}


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def fmt_task(task, index: int = None) -> str:
    prefix = f"{index:>2}. " if index is not None else "   "
    due    = task.due_date.strftime("%b %d") if task.due_date else "no due date"
    today  = date.today()
    if task.due_date and task.due_date < today:
        due = color(f"OVERDUE ({due})", RED)
    elif task.due_date == today:
        due = color(f"TODAY ({due})", YELLOW)

    p_label = PRIORITY_LABELS[task.priority]
    p_color = PRIORITY_COLORS[task.priority]
    return (
        f"{prefix}{color(task.title, BOLD)}\n"
        f"      id={color(task.id, DIM)}  "
        f"priority={color(p_label, p_color)}  "
        f"due={due}"
        + (f"\n      notes: {task.notes}" if task.notes else "")
    )


# ── Command handlers ───────────────────────────────────────────────────────────

def cmd_add(args, mgr: TaskManager) -> None:
    due = None
    if args.due:
        try:
            due = date.fromisoformat(args.due)
        except ValueError:
            print(color("Error: --due must be YYYY-MM-DD", RED))
            sys.exit(1)
    task = mgr.add(args.title, priority=args.priority, due_date=due, notes=args.notes or "")
    print(color(f"\n✅ Added task [{task.id}]: {task.title}", GREEN))


def cmd_list(args, mgr: TaskManager) -> None:
    tasks = mgr.list_tasks()
    if not tasks:
        print(color("\nNo tasks! Add one with:  python main.py add \"My task\"", DIM))
        return
    print(color(f"\n{'─'*50}", DIM))
    print(color(f"  📋  TaskFlow  ({len(tasks)} task{'s' if len(tasks)!=1 else ''})", BOLD))
    print(color(f"{'─'*50}", DIM))
    for i, t in enumerate(tasks, 1):
        print(fmt_task(t, i))
    print(color(f"{'─'*50}\n", DIM))


def cmd_next(args, mgr: TaskManager) -> None:
    task = mgr.peek_next()
    if not task:
        print(color("\nNo tasks pending.", DIM))
        return
    print(color("\n🎯  Next up:", BOLD))
    print(fmt_task(task))
    print()


def cmd_complete(args, mgr: TaskManager) -> None:
    try:
        task = mgr.complete(args.id)
        print(color(f"\n🎉 Completed: {task.title}", GREEN))
    except KeyError as e:
        print(color(f"\nError: {e}", RED))
        sys.exit(1)


def cmd_delete(args, mgr: TaskManager) -> None:
    try:
        task = mgr.delete(args.id)
        print(color(f"\n🗑  Deleted: {task.title}", YELLOW))
    except KeyError as e:
        print(color(f"\nError: {e}", RED))
        sys.exit(1)


def cmd_snooze(args, mgr: TaskManager) -> None:
    try:
        task = mgr.snooze(args.id, days=args.days)
        new_due = task.due_date.strftime("%b %d, %Y") if task.due_date else "unknown"
        print(color(f"\n😴 Snoozed '{task.title}' — new due date: {new_due}", CYAN))
    except KeyError as e:
        print(color(f"\nError: {e}", RED))
        sys.exit(1)


def cmd_stats(args, mgr: TaskManager) -> None:
    s = mgr.stats()
    print(color(f"\n{'─'*40}", DIM))
    print(color("  📊  TaskFlow Stats", BOLD))
    print(color(f"{'─'*40}", DIM))
    print(f"  Total active tasks : {color(str(s['total']), BOLD)}")
    print(f"  Overdue            : {color(str(s['overdue']), RED if s['overdue'] else GREEN)}")
    print()
    print("  By priority:")
    for p, label in PRIORITY_LABELS.items():
        count = s["by_priority"][p]
        bar   = color("█" * count, PRIORITY_COLORS[p]) if count else DIM + "─" + RESET
        print(f"    {label:<18} {bar}  {count}")
    print(color(f"{'─'*40}\n", DIM))


# ── Argument parser ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description="TaskFlow — a priority-scheduled CLI task manager.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task description")
    p_add.add_argument("--priority", "-p", type=int, default=3,
                       metavar="1-5", help="1=critical … 5=someday (default: 3)")
    p_add.add_argument("--due", "-d", metavar="YYYY-MM-DD", help="Due date")
    p_add.add_argument("--notes", "-n", help="Optional notes")

    # list
    sub.add_parser("list", help="List all tasks sorted by priority")

    # next
    sub.add_parser("next", help="Show the single highest-priority task")

    # complete
    p_done = sub.add_parser("complete", help="Mark a task as done")
    p_done.add_argument("id", help="Task ID (first 8 chars shown in list)")

    # delete
    p_del = sub.add_parser("delete", help="Remove a task permanently")
    p_del.add_argument("id", help="Task ID")

    # snooze
    p_snooze = sub.add_parser("snooze", help="Push a task's due date forward")
    p_snooze.add_argument("id", help="Task ID")
    p_snooze.add_argument("--days", type=int, default=1, help="Days to snooze (default: 1)")

    # stats
    sub.add_parser("stats", help="Show a summary of your task list")

    return parser


HANDLERS = {
    "add":      cmd_add,
    "list":     cmd_list,
    "next":     cmd_next,
    "complete": cmd_complete,
    "delete":   cmd_delete,
    "snooze":   cmd_snooze,
    "stats":    cmd_stats,
}


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()
    mgr    = TaskManager()
    HANDLERS[args.command](args, mgr)


if __name__ == "__main__":
    main()

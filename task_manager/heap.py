"""
heap.py -- Min-Heap implementation from scratch

A min-heap is a complete binary tree stored as a list where every
parent node is <= its children.  This guarantees O(1) peek at the
minimum element and O(log n) insertions / deletions.

                  [0]         <- index 0  (root / minimum)
                 /   \
               [1]   [2]      <- indices 1, 2
              /  \   /  \
            [3] [4] [5] [6]   <- indices 3-6

Parent of node i  -> (i - 1) // 2
Left child of i   -> 2*i + 1
Right child of i  -> 2*i + 2

Time complexities
-----------------
push      O(log n)
pop       O(log n)
peek      O(1)
heapify   O(n)         ← build heap from existing list
"""

from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")   # T must support __lt__ for comparisons


class MinHeap(Generic[T]):
    """Generic min-heap. Works with any type that defines __lt__."""

    def __init__(self) -> None:
        self._data: List[T] = []

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def push(self, item: T) -> None:
        """Insert item and restore the heap property.  O(log n)."""
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> T:
        """Remove and return the minimum item.  O(log n)."""
        if not self._data:
            raise IndexError("pop from empty heap")

        # Swap root with last element, shrink list, then sift root down.
        self._swap(0, len(self._data) - 1)
        minimum = self._data.pop()
        if self._data:
            self._sift_down(0)
        return minimum

    def peek(self) -> T:
        """Return (but don't remove) the minimum item.  O(1)."""
        if not self._data:
            raise IndexError("peek at empty heap")
        return self._data[0]

    def heapify(self, items: List[T]) -> None:
        """Build a heap from an existing list in O(n) time.

        We start from the last internal node (index n//2 - 1) and
        sift every node downward, which is mathematically O(n).
        """
        self._data = list(items)
        start = len(self._data) // 2 - 1
        for i in range(start, -1, -1):
            self._sift_down(i)

    def remove_by(self, predicate) -> Optional[T]:
        """Remove the first item matching predicate.  O(n)."""
        for i, item in enumerate(self._data):
            if predicate(item):
                # Replace with last element, shrink, then fix heap.
                self._swap(i, len(self._data) - 1)
                removed = self._data.pop()
                if i < len(self._data):
                    self._sift_up(i)
                    self._sift_down(i)
                return removed
        return None

    def to_sorted_list(self) -> List[T]:
        """Return a sorted copy without mutating the heap.  O(n log n)."""
        clone = MinHeap()
        clone.heapify(self._data)
        return [clone.pop() for _ in range(len(clone))]

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i: int) -> None:
        """Bubble item at index i upward until heap property is restored."""
        while i > 0:
            parent = self._parent(i)
            if self._data[i] < self._data[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """Push item at index i downward until heap property is restored."""
        n = len(self._data)
        while True:
            smallest = i
            left  = self._left(i)
            right = self._right(i)

            if left < n and self._data[left] < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right

            if smallest == i:
                break

            self._swap(i, smallest)
            i = smallest

"""
Heaps Module
Manual array-based implementation of:
- MinHeap (parent <= children)
- MaxHeap (parent >= children)
- Heapify-Up (percolate up) & Heapify-Down (sift down)
- In-place Build-Heap in O(n)
- Heap Sort algorithm
"""

from typing import List, Any, Optional, Dict


class MinHeap:
    """Manual Array-based Binary Min-Heap (0-indexed)."""

    def __init__(self):
        self.heap: List[Any] = []

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        return 2 * i + 2

    def insert(self, val: Any) -> None:
        """Insert value: O(log n)."""
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)

    def extract_min(self) -> Optional[Any]:
        """Extract minimum value from root: O(log n)."""
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return min_val

    def peek(self) -> Optional[Any]:
        return self.heap[0] if self.heap else None

    def _heapify_up(self, index: int) -> None:
        while index > 0 and self.heap[index] < self.heap[self._parent(index)]:
            p = self._parent(index)
            self.heap[index], self.heap[p] = self.heap[p], self.heap[index]
            index = p

    def _heapify_down(self, index: int) -> None:
        size = len(self.heap)
        smallest = index
        left = self._left_child(index)
        right = self._right_child(index)

        if left < size and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < size and self.heap[right] < self.heap[smallest]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def build_heap(self, array: List[Any]) -> None:
        """Build heap from arbitrary array in O(n) time."""
        self.heap = list(array)
        for i in range((len(self.heap) // 2) - 1, -1, -1):
            self._heapify_down(i)

    def size(self) -> int:
        return len(self.heap)

    def to_list(self) -> List[Any]:
        return list(self.heap)


class MaxHeap:
    """Manual Array-based Binary Max-Heap (0-indexed)."""

    def __init__(self):
        self.heap: List[Any] = []

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        return 2 * i + 2

    def insert(self, val: Any) -> None:
        """Insert value: O(log n)."""
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)

    def extract_max(self) -> Optional[Any]:
        """Extract maximum value from root: O(log n)."""
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        max_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return max_val

    def peek(self) -> Optional[Any]:
        return self.heap[0] if self.heap else None

    def _heapify_up(self, index: int) -> None:
        while index > 0 and self.heap[index] > self.heap[self._parent(index)]:
            p = self._parent(index)
            self.heap[index], self.heap[p] = self.heap[p], self.heap[index]
            index = p

    def _heapify_down(self, index: int) -> None:
        size = len(self.heap)
        largest = index
        left = self._left_child(index)
        right = self._right_child(index)

        if left < size and self.heap[left] > self.heap[largest]:
            largest = left
        if right < size and self.heap[right] > self.heap[largest]:
            largest = right

        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self._heapify_down(largest)

    def build_heap(self, array: List[Any]) -> None:
        """Build heap from arbitrary array in O(n) time."""
        self.heap = list(array)
        for i in range((len(self.heap) // 2) - 1, -1, -1):
            self._heapify_down(i)

    def size(self) -> int:
        return len(self.heap)

    def to_list(self) -> List[Any]:
        return list(self.heap)


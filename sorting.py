"""
Sorting Module
Manual implementation of the six classic sorting algorithms:
1. Bubble Sort
2. Selection Sort
3. Insertion Sort
4. Merge Sort
5. Quick Sort
6. Heap Sort (using array-based max heap logic)

Each returns the sorted list, step metrics (comparisons, swaps), and complexities.
"""

from typing import List, Any, Dict, Tuple
from heaps import MaxHeap


class SortingAlgorithms:
    """Demonstrates all 6 major sorting algorithms with operation counters."""

    @staticmethod
    def bubble_sort(arr: List[Any]) -> Dict[str, Any]:
        """
        Bubble Sort: repeatedly swap adjacent elements out of order.
        Time: Best O(n), Avg O(n^2), Worst O(n^2)
        Space: O(1)
        """
        a = list(arr)
        n = len(a)
        comparisons = 0
        swaps = 0

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                comparisons += 1
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swaps += 1
                    swapped = True
            if not swapped:
                break

        return {
            "algorithm": "Bubble Sort",
            "sorted": a,
            "comparisons": comparisons,
            "swaps": swaps,
            "time_complexity": "O(n^2) worst/avg, O(n) best",
            "space_complexity": "O(1)"
        }

    @staticmethod
    def selection_sort(arr: List[Any]) -> Dict[str, Any]:
        """
        Selection Sort: find minimum from unsorted part and place at beginning.
        Time: O(n^2) all cases
        Space: O(1)
        """
        a = list(arr)
        n = len(a)
        comparisons = 0
        swaps = 0

        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                comparisons += 1
                if a[j] < a[min_idx]:
                    min_idx = j
            if min_idx != i:
                a[i], a[min_idx] = a[min_idx], a[i]
                swaps += 1

        return {
            "algorithm": "Selection Sort",
            "sorted": a,
            "comparisons": comparisons,
            "swaps": swaps,
            "time_complexity": "O(n^2)",
            "space_complexity": "O(1)"
        }

    @staticmethod
    def insertion_sort(arr: List[Any]) -> Dict[str, Any]:
        """
        Insertion Sort: build sorted array one item at a time.
        Time: Best O(n), Avg O(n^2), Worst O(n^2)
        Space: O(1)
        """
        a = list(arr)
        n = len(a)
        comparisons = 0
        shifts = 0

        for i in range(1, n):
            key = a[i]
            j = i - 1
            while j >= 0:
                comparisons += 1
                if a[j] > key:
                    a[j + 1] = a[j]
                    shifts += 1
                    j -= 1
                else:
                    break
            a[j + 1] = key

        return {
            "algorithm": "Insertion Sort",
            "sorted": a,
            "comparisons": comparisons,
            "shifts": shifts,
            "time_complexity": "O(n^2) worst/avg, O(n) best",
            "space_complexity": "O(1)"
        }

    @staticmethod
    def merge_sort(arr: List[Any]) -> Dict[str, Any]:
        """
        Merge Sort: Divide and Conquer.
        Time: O(n log n) all cases
        Space: O(n)
        """
        a = list(arr)
        comparisons = [0]

        def _merge_sort_rec(sub: List[Any]) -> List[Any]:
            if len(sub) <= 1:
                return sub
            mid = len(sub) // 2
            left = _merge_sort_rec(sub[:mid])
            right = _merge_sort_rec(sub[mid:])

            merged = []
            i = j = 0
            while i < len(left) and j < len(right):
                comparisons[0] += 1
                if left[i] <= right[j]:
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
            merged.extend(left[i:])
            merged.extend(right[j:])
            return merged

        sorted_arr = _merge_sort_rec(a)

        return {
            "algorithm": "Merge Sort",
            "sorted": sorted_arr,
            "comparisons": comparisons[0],
            "time_complexity": "O(n log n)",
            "space_complexity": "O(n)"
        }

    @staticmethod
    def quick_sort(arr: List[Any]) -> Dict[str, Any]:
        """
        Quick Sort: partition around pivot element.
        Time: Best/Avg O(n log n), Worst O(n^2)
        Space: O(log n) call stack
        """
        a = list(arr)
        metrics = {"comparisons": 0, "swaps": 0}

        def _partition(low: int, high: int) -> int:
            pivot = a[high]
            i = low - 1
            for j in range(low, high):
                metrics["comparisons"] += 1
                if a[j] <= pivot:
                    i += 1
                    a[i], a[j] = a[j], a[i]
                    metrics["swaps"] += 1
            a[i + 1], a[high] = a[high], a[i + 1]
            metrics["swaps"] += 1
            return i + 1

        def _quick_sort_rec(low: int, high: int):
            if low < high:
                pi = _partition(low, high)
                _quick_sort_rec(low, pi - 1)
                _quick_sort_rec(pi + 1, high)

        _quick_sort_rec(0, len(a) - 1)

        return {
            "algorithm": "Quick Sort",
            "sorted": a,
            "comparisons": metrics["comparisons"],
            "swaps": metrics["swaps"],
            "time_complexity": "O(n log n) avg, O(n^2) worst",
            "space_complexity": "O(log n)"
        }

    @staticmethod
    def heap_sort(arr: List[Any]) -> Dict[str, Any]:
        """
        Heap Sort: In-place Max-Heap sort.
        Time: O(n log n) all cases
        Space: O(1)
        """
        a = list(arr)
        n = len(a)
        metrics = {"comparisons": 0, "swaps": 0}

        def _heapify(size: int, i: int):
            largest = i
            l = 2 * i + 1
            r = 2 * i + 2

            if l < size:
                metrics["comparisons"] += 1
                if a[l] > a[largest]:
                    largest = l

            if r < size:
                metrics["comparisons"] += 1
                if a[r] > a[largest]:
                    largest = r

            if largest != i:
                a[i], a[largest] = a[largest], a[i]
                metrics["swaps"] += 1
                _heapify(size, largest)

        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            _heapify(n, i)

        # Extract elements one by one
        for i in range(n - 1, 0, -1):
            a[i], a[0] = a[0], a[i]
            metrics["swaps"] += 1
            _heapify(i, 0)

        return {
            "algorithm": "Heap Sort",
            "sorted": a,
            "comparisons": metrics["comparisons"],
            "swaps": metrics["swaps"],
            "time_complexity": "O(n log n)",
            "space_complexity": "O(1)"
        }


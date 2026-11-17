"""
Searching Module
Implements:
- Linear Search
- Binary Search (Iterative and Recursive)
- BST Search
Tracks comparison counts and step-by-step trace for educational/DSA lab demonstration.
"""

from typing import List, Any, Optional, Dict
from trees import BinarySearchTree


class SearchingAlgorithms:
    """Manual searching algorithms with step-by-step tracing."""

    @staticmethod
    def linear_search(arr: List[Any], target: Any) -> Dict[str, Any]:
        """
        Linear Search on unsorted/sorted list.
        Time Complexity: Best O(1), Worst O(n), Average O(n)
        Space Complexity: O(1)
        """
        comparisons = 0
        steps = []
        found_idx = -1

        for idx, val in enumerate(arr):
            comparisons += 1
            steps.append({"index": idx, "value": val, "match": val == target})
            if val == target:
                found_idx = idx
                break

        return {
            "target": target,
            "found": found_idx != -1,
            "index": found_idx,
            "comparisons": comparisons,
            "steps": steps,
            "algorithm": "Linear Search",
            "time_complexity": "O(n)",
            "space_complexity": "O(1)"
        }

    @staticmethod
    def binary_search(arr: List[Any], target: Any) -> Dict[str, Any]:
        """
        Binary Search on sorted list.
        Time Complexity: Best O(1), Worst O(log n), Average O(log n)
        Space Complexity: O(1)
        """
        # Ensure array is sorted (for simulation, check if sorted)
        is_sorted = all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
        working_arr = list(arr)
        if not is_sorted:
            working_arr.sort()

        low = 0
        high = len(working_arr) - 1
        comparisons = 0
        steps = []
        found_idx = -1

        while low <= high:
            mid = (low + high) // 2
            mid_val = working_arr[mid]
            comparisons += 1

            steps.append({
                "low": low,
                "high": high,
                "mid": mid,
                "mid_val": mid_val
            })

            if mid_val == target:
                found_idx = mid
                break
            elif mid_val < target:
                low = mid + 1
            else:
                high = mid - 1

        return {
            "target": target,
            "found": found_idx != -1,
            "index": found_idx,
            "was_sorted": is_sorted,
            "array_searched": working_arr,
            "comparisons": comparisons,
            "steps": steps,
            "algorithm": "Binary Search",
            "time_complexity": "O(log n)",
            "space_complexity": "O(1)"
        }

    @staticmethod
    def bst_search(values: List[Any], target: Any) -> Dict[str, Any]:
        """Constructs a BST from values and searches for target."""
        bst = BinarySearchTree()
        for v in values:
            bst.insert(v)

        curr = bst.root
        comparisons = 0
        steps = []
        found = False

        while curr is not None:
            comparisons += 1
            steps.append({"current_node": curr.key, "target": target})
            if curr.key == target:
                found = True
                break
            elif target < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        return {
            "target": target,
            "found": found,
            "comparisons": comparisons,
            "steps": steps,
            "algorithm": "BST Search",
            "time_complexity": "O(h) ~ O(log n) avg, O(n) worst",
            "space_complexity": "O(n)"
        }


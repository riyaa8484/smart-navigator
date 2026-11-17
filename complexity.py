"""
Complexity Analysis Module
Provides comprehensive time and space complexity data for all DSA algorithms
and data structures implemented across the project.
"""

from typing import Dict, Any, Optional

COMPLEXITY_DATABASE: Dict[str, Dict[str, Any]] = {
    "bfs": {
        "name": "Breadth-First Search",
        "category": "Graph",
        "time_best": "O(1)",
        "time_average": "O(V + E)",
        "time_worst": "O(V + E)",
        "space_complexity": "O(V)",
        "description": "Explores graph level-by-level using a FIFO queue. Guarantees shortest path in unweighted graphs.",
        "use_case": "Finding shortest-hop routes, peer-to-peer torrent finding, web crawling."
    },
    "dfs": {
        "name": "Depth-First Search",
        "category": "Graph",
        "time_best": "O(1)",
        "time_average": "O(V + E)",
        "time_worst": "O(V + E)",
        "space_complexity": "O(V)",
        "description": "Explores as deep as possible along each branch before backtracking using a LIFO stack.",
        "use_case": "Cycle detection, topological sorting, maze solving, connected components."
    },
    "dijkstra": {
        "name": "Dijkstra's Algorithm",
        "category": "Graph",
        "time_best": "O(V^2) or O((V + E) log V)",
        "time_average": "O(V^2) with array / O((V + E) log V) with min-heap",
        "time_worst": "O(V^2)",
        "space_complexity": "O(V)",
        "description": "Greedy algorithm to find shortest path from single source in non-negative edge weighted graphs.",
        "use_case": "GPS road routing, network routing protocols (OSPF, IS-IS)."
    },
    "prim": {
        "name": "Prim's MST Algorithm",
        "category": "Graph",
        "time_best": "O(V^2)",
        "time_average": "O(V^2) or O(E log V)",
        "time_worst": "O(V^2)",
        "space_complexity": "O(V)",
        "description": "Grows a Minimum Spanning Tree vertex by vertex by adding the cheapest cut edge.",
        "use_case": "Dense graph network cable laying, electrical grid design."
    },
    "kruskal": {
        "name": "Kruskal's MST Algorithm",
        "category": "Graph",
        "time_best": "O(E log E)",
        "time_average": "O(E log E)",
        "time_worst": "O(E log E)",
        "space_complexity": "O(V + E)",
        "description": "Greedy edge-sorting algorithm using Disjoint Set Union (Union-Find) with path compression.",
        "use_case": "Sparse graph road network optimization, pipeline networks."
    },
    "bubble": {
        "name": "Bubble Sort",
        "category": "Sorting",
        "time_best": "O(n)",
        "time_average": "O(n^2)",
        "time_worst": "O(n^2)",
        "space_complexity": "O(1)",
        "description": "Repeatedly steps through list, compares adjacent elements and swaps them if out of order.",
        "use_case": "Educational demonstration; detecting already sorted lists."
    },
    "selection": {
        "name": "Selection Sort",
        "category": "Sorting",
        "time_best": "O(n^2)",
        "time_average": "O(n^2)",
        "time_worst": "O(n^2)",
        "space_complexity": "O(1)",
        "description": "Divides list into sorted and unsorted parts; repeatedly selects minimum from unsorted part.",
        "use_case": "When memory write operations are expensive (does at most O(n) swaps)."
    },
    "insertion": {
        "name": "Insertion Sort",
        "category": "Sorting",
        "time_best": "O(n)",
        "time_average": "O(n^2)",
        "time_worst": "O(n^2)",
        "space_complexity": "O(1)",
        "description": "Builds sorted array element by element by inserting each item into its correct slot.",
        "use_case": "Small arrays (n <= 50) and nearly sorted data streams."
    },
    "merge": {
        "name": "Merge Sort",
        "category": "Sorting",
        "time_best": "O(n log n)",
        "time_average": "O(n log n)",
        "time_worst": "O(n log n)",
        "space_complexity": "O(n)",
        "description": "Stable Divide-and-Conquer algorithm that divides array in halves, sorts, and merges.",
        "use_case": "Linked list sorting, external tape/disk sorting, guaranteed O(n log n) requirements."
    },
    "quick": {
        "name": "Quick Sort",
        "category": "Sorting",
        "time_best": "O(n log n)",
        "time_average": "O(n log n)",
        "time_worst": "O(n^2)",
        "space_complexity": "O(log n)",
        "description": "Divides array around pivot element so items smaller go left and larger go right.",
        "use_case": "General in-memory fast sorting with excellent cache locality."
    },
    "heap": {
        "name": "Heap Sort",
        "category": "Sorting",
        "time_best": "O(n log n)",
        "time_average": "O(n log n)",
        "time_worst": "O(n log n)",
        "space_complexity": "O(1)",
        "description": "Transforms array into Max-Heap and repeatedly extracts root to back of array.",
        "use_case": "Embedded systems where O(1) auxiliary memory and guaranteed O(n log n) are needed."
    },
    "linear_search": {
        "name": "Linear Search",
        "category": "Searching",
        "time_best": "O(1)",
        "time_average": "O(n)",
        "time_worst": "O(n)",
        "space_complexity": "O(1)",
        "description": "Sequentially inspects each item until match is found.",
        "use_case": "Unsorted lists or tiny datasets."
    },
    "binary_search": {
        "name": "Binary Search",
        "category": "Searching",
        "time_best": "O(1)",
        "time_average": "O(log n)",
        "time_worst": "O(log n)",
        "space_complexity": "O(1)",
        "description": "Halves search interval at each step on a monotonically sorted array.",
        "use_case": "Large static sorted arrays, lookup tables."
    },
    "bst": {
        "name": "Binary Search Tree Operations",
        "category": "Trees",
        "time_best": "O(1)",
        "time_average": "O(log n)",
        "time_worst": "O(n)",
        "space_complexity": "O(n)",
        "description": "Binary tree where left children < node < right children.",
        "use_case": "Dynamic key-value sets with ordered traversals."
    },
    "hashing": {
        "name": "Hash Table Lookups",
        "category": "Hashing",
        "time_best": "O(1)",
        "time_average": "O(1)",
        "time_worst": "O(n)",
        "space_complexity": "O(n)",
        "description": "Maps keys to array indices via hash function with chaining or linear probing.",
        "use_case": "Constant-time dictionary, database indexing, caching."
    },
    "stack": {
        "name": "Stack Push/Pop",
        "category": "Stacks",
        "time_best": "O(1)",
        "time_average": "O(1)",
        "time_worst": "O(1)",
        "space_complexity": "O(n)",
        "description": "Last-In-First-Out data structure.",
        "use_case": "Function call stack, undo operations, parenthesis matching, expression parsing."
    },
    "circular_queue": {
        "name": "Circular Queue",
        "category": "Queues",
        "time_best": "O(1)",
        "time_average": "O(1)",
        "time_worst": "O(1)",
        "space_complexity": "O(n)",
        "description": "FIFO queue with fixed buffer and modulo wraparound.",
        "use_case": "Traffic buffers, CPU scheduling, audio streaming ring buffers."
    }
}


def get_complexity(algorithm_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve complexity details for given algorithm name (case-insensitive)."""
    key = algorithm_name.strip().lower()
    return COMPLEXITY_DATABASE.get(key)


def get_all_complexities() -> Dict[str, Dict[str, Any]]:
    """Return complete dictionary of all registered DSA algorithms."""
    return COMPLEXITY_DATABASE


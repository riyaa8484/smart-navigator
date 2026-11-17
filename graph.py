"""
Graph Data Structure Module
Implements Adjacency List, Adjacency Matrix, BFS, DFS, Dijkstra, Prim's MST,
and Kruskal's MST (with custom Disjoint Set Union) purely in manual Python.
No external or built-in DSA libraries (e.g. heapq, collections.deque) are used.
"""

from typing import Dict, List, Tuple, Any, Optional, Set
import json
import os
import math


class DisjointSetUnion:
    """Disjoint Set Union (DSU / Union-Find) with path compression and union by rank."""

    def __init__(self, elements: List[str]):
        self.parent: Dict[str, str] = {e: e for e in elements}
        self.rank: Dict[str, int] = {e: 0 for e in elements}

    def find(self, item: str) -> str:
        """Find representative with path compression: O(alpha(V)) ~ O(1) amortized."""
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, root1: str, root2: str) -> bool:
        """Union two sets by rank. Returns True if merged, False if already in same set."""
        p1 = self.find(root1)
        p2 = self.find(root2)
        if p1 == p2:
            return False
        if self.rank[p1] < self.rank[p2]:
            self.parent[p1] = p2
        elif self.rank[p1] > self.rank[p2]:
            self.parent[p2] = p1
        else:
            self.parent[p2] = p1
            self.rank[p1] += 1
        return True


class CampusGraph:
    """
    Manual Graph Implementation supporting:
    - Adjacency List representation
    - Adjacency Matrix representation
    - Breadth-First Search (BFS) for shortest unweighted / minimum edge routes
    - Depth-First Search (DFS) for reachable paths
    - Dijkstra's algorithm for shortest weighted paths
    - Prim's MST algorithm
    - Kruskal's MST algorithm
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}  # node_code -> metadata {name, coords, category, ...}
        self.adj_list: Dict[str, List[Tuple[str, float]]] = {}  # node_code -> list of (neighbor_code, weight)
        self.edges: List[Tuple[str, str, float]] = []  # list of (u, v, weight)

    @classmethod
    def load_from_json(cls, json_path: str) -> "CampusGraph":
        """Factory method to populate graph from a JSON file."""
        graph = cls()
        if not os.path.exists(json_path):
            return graph

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for loc in data.get("locations", []):
            code = loc.get("code", str(loc.get("id")))
            graph.add_node(code, {
                "id": loc.get("id"),
                "name": loc.get("name"),
                "category": loc.get("category"),
                "coords": loc.get("coords"),
                "description": loc.get("description", "")
            })

        for edge in data.get("edges", []):
            u = edge.get("source")
            v = edge.get("target")
            w = float(edge.get("weight", 1.0))
            graph.add_edge(u, v, w, bidirectional=True)

        return graph

    def add_node(self, node_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a vertex to the graph."""
        if node_id not in self.nodes:
            self.nodes[node_id] = metadata or {}
            self.adj_list[node_id] = []

    def add_edge(self, u: str, v: str, weight: float = 1.0, bidirectional: bool = True) -> None:
        """Add a weighted edge between two nodes."""
        if u not in self.nodes:
            self.add_node(u)
        if v not in self.nodes:
            self.add_node(v)

        # Avoid duplicate edges in adjacency list
        if not any(neighbor == v for neighbor, _ in self.adj_list[u]):
            self.adj_list[u].append((v, weight))
            self.edges.append((u, v, weight))

        if bidirectional:
            if not any(neighbor == u for neighbor, _ in self.adj_list[v]):
                self.adj_list[v].append((u, weight))

    def get_adjacency_list(self) -> Dict[str, List[str]]:
        """Return simplified adjacency list with neighbor node codes."""
        return {node: [neighbor for neighbor, _ in neighbors] for node, neighbors in self.adj_list.items()}

    def get_weighted_adjacency_list(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return adjacency list with edge weights."""
        return {
            node: [{"node": nbr, "weight": w} for nbr, w in neighbors]
            for node, neighbors in self.adj_list.items()
        }

    def get_adjacency_matrix(self) -> Dict[str, Any]:
        """
        Convert graph to 2D Adjacency Matrix.
        Returns:
            {
                "nodes": list of node names in row/col order,
                "matrix": 2D list where M[i][j] = edge weight or 0
            }
        """
        node_keys = sorted(list(self.nodes.keys()))
        n = len(node_keys)
        key_to_idx = {k: i for i, k in enumerate(node_keys)}

        matrix: List[List[float]] = [[0.0] * n for _ in range(n)]

        for u in self.adj_list:
            u_idx = key_to_idx[u]
            for v, weight in self.adj_list[u]:
                v_idx = key_to_idx[v]
                matrix[u_idx][v_idx] = round(weight, 4)

        return {
            "nodes": node_keys,
            "matrix": matrix,
            "size": n
        }

    def bfs_shortest_path(self, start: str, end: str) -> Dict[str, Any]:
        """
        Breadth-First Search (BFS) to find path with minimum number of edge hops.
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        """
        if start not in self.nodes or end not in self.nodes:
            return {"found": False, "path": [], "distance": 0.0, "visited_order": [], "error": "Invalid start or end node"}

        if start == end:
            return {"found": True, "path": [start], "distance": 0.0, "visited_order": [start], "hops": 0}

        # Manual queue using a list and front pointer (avoids collections.deque)
        queue: List[str] = [start]
        front_idx = 0
        visited: Set[str] = {start}
        parent: Dict[str, Optional[str]] = {start: None}
        visited_order: List[str] = []

        found = False
        while front_idx < len(queue):
            curr = queue[front_idx]
            front_idx += 1
            visited_order.append(curr)

            if curr == end:
                found = True
                break

            for neighbor, _ in self.adj_list.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = curr
                    queue.append(neighbor)

        if not found:
            return {"found": False, "path": [], "distance": 0.0, "visited_order": visited_order}

        # Reconstruct path from end to start
        path: List[str] = []
        curr_node: Optional[str] = end
        while curr_node is not None:
            path.append(curr_node)
            curr_node = parent.get(curr_node)
        path.reverse()

        # Calculate total distance along path
        total_dist = self._calculate_path_distance(path)

        return {
            "found": True,
            "path": path,
            "hops": len(path) - 1,
            "distance": round(total_dist, 3),
            "visited_order": visited_order,
            "algorithm": "BFS (Minimum Edge Route)",
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)"
        }

    def dfs_path(self, start: str, end: str) -> Dict[str, Any]:
        """
        Depth-First Search (DFS) path search using manual stack.
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        """
        if start not in self.nodes or end not in self.nodes:
            return {"found": False, "path": [], "visited_order": [], "error": "Invalid start or end node"}

        stack: List[str] = [start]
        visited: Set[str] = set()
        parent: Dict[str, Optional[str]] = {start: None}
        visited_order: List[str] = []

        found = False
        while len(stack) > 0:
            curr = stack.pop()  # Manual LIFO
            if curr in visited:
                continue
            visited.add(curr)
            visited_order.append(curr)

            if curr == end:
                found = True
                break

            # Add neighbors in reverse so leftmost is processed first
            for neighbor, _ in reversed(self.adj_list.get(curr, [])):
                if neighbor not in visited:
                    if neighbor not in parent:
                        parent[neighbor] = curr
                    stack.append(neighbor)

        if not found:
            return {"found": False, "path": [], "distance": 0.0, "visited_order": visited_order}

        path: List[str] = []
        curr_node: Optional[str] = end
        while curr_node is not None:
            path.append(curr_node)
            curr_node = parent.get(curr_node)
        path.reverse()

        total_dist = self._calculate_path_distance(path)

        return {
            "found": True,
            "path": path,
            "distance": round(total_dist, 3),
            "visited_order": visited_order,
            "algorithm": "DFS Path Search",
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)"
        }

    def dijkstra_shortest_path(self, start: str, end: str) -> Dict[str, Any]:
        """
        Dijkstra's Algorithm for shortest weighted path.
        Implemented with manual min selection over unvisited nodes: O(V^2) or O(V log V).
        """
        if start not in self.nodes or end not in self.nodes:
            return {"found": False, "path": [], "distance": float("inf"), "error": "Invalid node"}

        distances: Dict[str, float] = {node: float("inf") for node in self.nodes}
        distances[start] = 0.0
        parent: Dict[str, Optional[str]] = {node: None for node in self.nodes}
        visited: Set[str] = set()

        all_nodes = set(self.nodes.keys())

        while len(visited) < len(all_nodes):
            # Find node in unvisited with smallest distance
            curr_min_node: Optional[str] = None
            min_dist = float("inf")
            for node in all_nodes:
                if node not in visited and distances[node] < min_dist:
                    min_dist = distances[node]
                    curr_min_node = node

            if curr_min_node is None or min_dist == float("inf"):
                break

            visited.add(curr_min_node)
            if curr_min_node == end:
                break

            for neighbor, weight in self.adj_list.get(curr_min_node, []):
                if neighbor not in visited:
                    new_dist = distances[curr_min_node] + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        parent[neighbor] = curr_min_node

        if distances[end] == float("inf"):
            return {"found": False, "path": [], "distance": float("inf")}

        path: List[str] = []
        curr_step: Optional[str] = end
        while curr_step is not None:
            path.append(curr_step)
            curr_step = parent[curr_step]
        path.reverse()

        return {
            "found": True,
            "path": path,
            "distance": round(distances[end], 3),
            "algorithm": "Dijkstra (Shortest Weighted Path)",
            "time_complexity": "O(V^2)",
            "space_complexity": "O(V)"
        }

    def prim_mst(self) -> Dict[str, Any]:
        """
        Prim's Algorithm for Minimum Spanning Tree (MST).
        Grows the MST starting from an arbitrary vertex.
        Time Complexity: O(V^2)
        Space Complexity: O(V + E)
        """
        if not self.nodes:
            return {"mst_edges": [], "total_weight": 0.0}

        start_node = next(iter(self.nodes))
        in_mst: Set[str] = {start_node}
        all_nodes = set(self.nodes.keys())
        mst_edges: List[List[Any]] = []
        total_weight = 0.0

        while len(in_mst) < len(all_nodes):
            min_edge: Optional[Tuple[str, str, float]] = None
            min_weight = float("inf")

            # Look for the minimum-weight edge connecting an MST node to a non-MST node
            for u in in_mst:
                for v, weight in self.adj_list.get(u, []):
                    if v not in in_mst and weight < min_weight:
                        min_weight = weight
                        min_edge = (u, v, weight)

            if min_edge is None:
                # Graph is disconnected
                break

            u, v, w = min_edge
            in_mst.add(v)
            mst_edges.append([u, v, round(w, 3)])
            total_weight += w

        return {
            "mst_edges": mst_edges,
            "total_weight": round(total_weight, 3),
            "edge_count": len(mst_edges),
            "vertex_count": len(in_mst),
            "algorithm": "Prim's Algorithm",
            "time_complexity": "O(V^2)",
            "space_complexity": "O(V)"
        }

    def kruskal_mst(self) -> Dict[str, Any]:
        """
        Kruskal's Algorithm for Minimum Spanning Tree (MST).
        Sorts edges and uses Disjoint Set Union (Union-Find) to detect cycles.
        Time Complexity: O(E log E)
        Space Complexity: O(V + E)
        """
        # Collect unique undirected edges
        unique_edges: List[Tuple[str, str, float]] = []
        seen_pairs: Set[Tuple[str, str]] = set()

        for u in self.adj_list:
            for v, w in self.adj_list[u]:
                pair = tuple(sorted([u, v]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_edges.append((pair[0], pair[1], w))

        # Manual Quick Sort / Merge Sort on edges by weight
        self._sort_edges_by_weight(unique_edges)

        dsu = DisjointSetUnion(list(self.nodes.keys()))
        mst_edges: List[List[Any]] = []
        total_weight = 0.0

        for u, v, w in unique_edges:
            if dsu.union(u, v):
                mst_edges.append([u, v, round(w, 3)])
                total_weight += w
                if len(mst_edges) == len(self.nodes) - 1:
                    break

        return {
            "mst_edges": mst_edges,
            "total_weight": round(total_weight, 3),
            "edge_count": len(mst_edges),
            "algorithm": "Kruskal's Algorithm",
            "time_complexity": "O(E log E)",
            "space_complexity": "O(V + E)"
        }

    def _sort_edges_by_weight(self, edges: List[Tuple[str, str, float]]) -> None:
        """In-place merge sort on edges by weight."""
        if len(edges) > 1:
            mid = len(edges) // 2
            left = edges[:mid]
            right = edges[mid:]

            self._sort_edges_by_weight(left)
            self._sort_edges_by_weight(right)

            i = j = k = 0
            while i < len(left) and j < len(right):
                if left[i][2] <= right[j][2]:
                    edges[k] = left[i]
                    i += 1
                else:
                    edges[k] = right[j]
                    j += 1
                k += 1

            while i < len(left):
                edges[k] = left[i]
                i += 1
                k += 1

            while j < len(right):
                edges[k] = right[j]
                j += 1
                k += 1

    def _calculate_path_distance(self, path: List[str]) -> float:
        """Helper to sum distances along a sequence of connected nodes."""
        dist = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            found_weight = 0.0
            for neighbor, w in self.adj_list.get(u, []):
                if neighbor == v:
                    found_weight = w
                    break
            dist += found_weight
        return dist


"""
Graph API Blueprint
Exposes Campus Graph Adjacency List, Adjacency Matrix, BFS, DFS, Dijkstra,
Prim's MST, and Kruskal's MST.
"""

from flask import Blueprint, jsonify, request
from config import Config
from graph import CampusGraph

graph_bp = Blueprint("graph_bp", __name__)


def _get_graph() -> CampusGraph:
    return CampusGraph.load_from_json(Config.CAMPUS_DATA_FILE)


@graph_bp.route("/api/graph/adjacency-list", methods=["GET"])
def get_adjacency_list():
    """Return campus graph adjacency list."""
    graph = _get_graph()
    return jsonify(graph.get_adjacency_list())


@graph_bp.route("/api/graph/adjacency-matrix", methods=["GET"])
def get_adjacency_matrix():
    """Return campus graph 2D adjacency matrix and node index ordering."""
    graph = _get_graph()
    return jsonify(graph.get_adjacency_matrix())


@graph_bp.route("/api/graph/bfs", methods=["POST"])
def graph_bfs():
    """
    Breadth-First Search (BFS) to find path with minimum edge hops.
    Request: { "start": "MainGate", "end": "Library" }
    """
    payload = request.get_json(force=True, silent=True) or {}
    start = payload.get("start")
    end = payload.get("end")

    if not start or not end:
        return jsonify({"error": "Fields 'start' and 'end' are required."}), 400

    graph = _get_graph()
    result = graph.bfs_shortest_path(start, end)
    return jsonify(result)


@graph_bp.route("/api/graph/dfs", methods=["POST"])
def graph_dfs():
    """
    Depth-First Search (DFS) path exploration.
    Request: { "start": "MainGate", "end": "Library" }
    """
    payload = request.get_json(force=True, silent=True) or {}
    start = payload.get("start")
    end = payload.get("end")

    if not start or not end:
        return jsonify({"error": "Fields 'start' and 'end' are required."}), 400

    graph = _get_graph()
    result = graph.dfs_path(start, end)
    return jsonify(result)


@graph_bp.route("/api/graph/dijkstra", methods=["POST"])
def graph_dijkstra():
    """Dijkstra's Algorithm for shortest weighted distance path."""
    payload = request.get_json(force=True, silent=True) or {}
    start = payload.get("start")
    end = payload.get("end")

    if not start or not end:
        return jsonify({"error": "Fields 'start' and 'end' are required."}), 400

    graph = _get_graph()
    result = graph.dijkstra_shortest_path(start, end)
    return jsonify(result)


@graph_bp.route("/api/graph/mst/prim", methods=["GET"])
def get_prim_mst():
    """Prim's Minimum Spanning Tree."""
    graph = _get_graph()
    return jsonify(graph.prim_mst())


@graph_bp.route("/api/graph/mst/kruskal", methods=["GET"])
def get_kruskal_mst():
    """Kruskal's Minimum Spanning Tree."""
    graph = _get_graph()
    return jsonify(graph.kruskal_mst())


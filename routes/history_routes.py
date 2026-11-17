"""
History API Blueprint
Exposes search history, back/forward stack navigation, and action undoing.
"""

from flask import Blueprint, jsonify, request
from history import HistoryManager
from config import Config

history_bp = Blueprint("history_bp", __name__)
history_mgr = HistoryManager(Config.HISTORY_DATA_FILE)


@history_bp.route("/api/history", methods=["GET"])
def get_history():
    """Retrieve search and navigation history."""
    limit = int(request.args.get("limit", 20))
    return jsonify(history_mgr.get_recent(limit=limit))


@history_bp.route("/api/history", methods=["POST"])
def add_history():
    """
    Record a new search in history.
    Request: { "src": "MainGate", "dst": "Library", "mode": "driving" }
    """
    payload = request.get_json(force=True, silent=True) or {}
    src = payload.get("src")
    dst = payload.get("dst")
    mode = payload.get("mode", "driving")
    metadata = {
        key: payload[key]
        for key in ("distance_km", "duration_min")
        if payload.get(key) is not None
    }

    if not src or not dst:
        return jsonify({"error": "Fields 'src' and 'dst' are required."}), 400

    rec = history_mgr.add_search(src, dst, mode, metadata=metadata)
    return jsonify({"success": True, "record": rec}), 201


@history_bp.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_history(record_id: int):
    """Delete a history entry by id."""
    success = history_mgr.delete_record(record_id)
    if success:
        return jsonify({"success": True, "deleted_id": record_id})
    return jsonify({"error": "Record not found."}), 404


@history_bp.route("/api/history/back", methods=["POST"])
def history_back():
    """Navigate backward in history stack."""
    record = history_mgr.back()
    if record:
        return jsonify({"success": True, "current": record})
    return jsonify({"success": False, "message": "No further backward history."})


@history_bp.route("/api/history/forward", methods=["POST"])
def history_forward():
    """Navigate forward in history stack."""
    record = history_mgr.forward()
    if record:
        return jsonify({"success": True, "current": record})
    return jsonify({"success": False, "message": "No further forward history."})


@history_bp.route("/api/history/undo", methods=["POST"])
def history_undo():
    """Undo the last recorded action."""
    result = history_mgr.undo_last_action()
    if result:
        return jsonify({"success": True, "undo": result})
    return jsonify({"success": False, "message": "Nothing to undo."})


@history_bp.route("/api/history/clear", methods=["POST"])
def history_clear():
    """Clear all history."""
    history_mgr.clear()
    return jsonify({"success": True, "message": "History cleared."})


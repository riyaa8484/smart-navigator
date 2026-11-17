"""
Campus Locations API Blueprint
Provides CRUD and search endpoints for campus locations.
"""

from flask import Blueprint, jsonify, request
import json
import os
from config import Config

location_bp = Blueprint("location_bp", __name__)


def _load_campus_data() -> dict:
    if os.path.exists(Config.CAMPUS_DATA_FILE):
        with open(Config.CAMPUS_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"campus_name": "Campus", "center": [28.6885, 77.1200], "locations": [], "edges": []}


def _save_campus_data(data: dict) -> None:
    with open(Config.CAMPUS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@location_bp.route("/api/locations", methods=["GET"])
def get_locations():
    """Retrieve all campus locations."""
    data = _load_campus_data()
    return jsonify(data.get("locations", []))


@location_bp.route("/api/locations/search", methods=["GET"])
def search_locations():
    """Search campus locations by query string ?q=Library"""
    query = request.args.get("q", "").strip().lower()
    data = _load_campus_data()
    locations = data.get("locations", [])

    if not query:
        return jsonify(locations)

    results = [
        loc for loc in locations
        if query in loc.get("name", "").lower()
        or query in loc.get("code", "").lower()
        or query in loc.get("category", "").lower()
        or query in loc.get("description", "").lower()
    ]
    return jsonify(results)


@location_bp.route("/api/locations", methods=["POST"])
def add_location():
    """Add a new campus location."""
    payload = request.get_json(force=True, silent=True) or {}
    name = payload.get("name")
    coords = payload.get("coords")

    if not name or not coords or len(coords) != 2:
        return jsonify({"error": "Fields 'name' and 'coords' [lat, lon] are required."}), 400

    data = _load_campus_data()
    locations = data.get("locations", [])

    new_id = payload.get("id") or (max([l.get("id", 0) for l in locations], default=0) + 1)
    code = payload.get("code") or name.replace(" ", "")

    new_loc = {
        "id": new_id,
        "code": code,
        "name": name,
        "category": payload.get("category", "general"),
        "coords": [float(coords[0]), float(coords[1])],
        "description": payload.get("description", "")
    }

    locations.append(new_loc)
    data["locations"] = locations
    _save_campus_data(data)

    return jsonify({"success": True, "location": new_loc}), 201


@location_bp.route("/api/locations/<int:loc_id>", methods=["DELETE"])
def delete_location(loc_id: int):
    """Delete a campus location by id."""
    data = _load_campus_data()
    locations = data.get("locations", [])
    initial_len = len(locations)

    data["locations"] = [loc for loc in locations if loc.get("id") != loc_id]

    if len(data["locations"]) == initial_len:
        return jsonify({"error": "Location not found."}), 404

    _save_campus_data(data)
    return jsonify({"success": True, "deleted_id": loc_id})


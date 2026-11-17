"""
Navigation API Blueprint
Exposes:
- Real-world place search via Photon API (GET /api/search?q=...)
- Reverse geocoding via Photon API (GET /api/reverse-geocode?lat=...&lon=...)
- Real road routing via OSRM with turn-by-turn steps (POST /api/route)
- Alternative route comparison (POST /api/route/alternatives)
- Route recommendation ranking (POST /api/route/recommend)
- Nearby mapped places query via Overpass API (GET /api/nearby)
"""

from flask import Blueprint, jsonify, request
from navigation import NavigationService
from recommendation import RouteRecommender

nav_bp = Blueprint("nav_bp", __name__)
nav_service = NavigationService()
recommender = RouteRecommender(nav_service)


@nav_bp.route("/api/search", methods=["GET"])
def search_places():
    """
    Search-as-you-type and place lookup via Photon API.
    Query params:
    ?q=India+Gate&limit=10&lat=28.6129&lon=77.2295
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    try:
        limit = min(max(int(request.args.get("limit", 10)), 1), 30)
    except (ValueError, TypeError):
        limit = 10

    lat_param = request.args.get("lat")
    lon_param = request.args.get("lon")
    lat = None
    lon = None
    if lat_param and lon_param:
        try:
            lat = float(lat_param)
            lon = float(lon_param)
        except (ValueError, TypeError):
            pass

    results = nav_service.search_locations(query, limit=limit, lat=lat, lon=lon)
    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": results
    })


@nav_bp.route("/api/reverse-geocode", methods=["GET"])
def reverse_geocode():
    """
    Reverse geocoding: convert (lat, lon) to place name and address.
    Query params: ?lat=28.6129&lon=77.2295
    """
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (ValueError, TypeError, KeyError):
        return jsonify({"error": "Valid floating point 'lat' and 'lon' query parameters are required."}), 400

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify({"error": "Latitude must be between -90 and 90, longitude between -180 and 180."}), 400

    result = nav_service.reverse_geocode(lat, lon)
    return jsonify(result), 200 if result.get("success") else 400


@nav_bp.route("/api/route", methods=["POST"])
def calculate_route():
    """
    Calculate road-following route between source and destination using OSRM.
    Accepts:
    - [lat, lon] coordinates: {"src": [28.6129, 77.2295], "dst": [28.6315, 77.2167], "mode": "driving"}
    - Place names / addresses: {"src": "India Gate", "dst": "Connaught Place", "mode": "walking"}
    - Campus codes for backward compatibility: {"src": "MainGate", "dst": "Library"}
    """
    payload = request.get_json(force=True, silent=True) or {}
    src = payload.get("src")
    dst = payload.get("dst")
    mode = payload.get("mode", "driving")

    if not src or not dst:
        return jsonify({"error": "Fields 'src' and 'dst' are required."}), 400

    # Validate coordinate bounds if passed as lists
    for point, label in [(src, "src"), (dst, "dst")]:
        if isinstance(point, (list, tuple)) and len(point) == 2:
            try:
                p_lat, p_lon = float(point[0]), float(point[1])
                if not (-90 <= p_lat <= 90 and -180 <= p_lon <= 180):
                    return jsonify({"error": f"Invalid coordinates for {label}: lat={p_lat}, lon={p_lon} out of range."}), 400
            except (ValueError, TypeError):
                return jsonify({"error": f"Coordinates for {label} must be numeric."}), 400

    # Valid modes
    valid_modes = ("driving", "walking", "walk", "foot", "cycling", "bike", "bicycle", "car")
    if mode.lower() not in valid_modes:
        return jsonify({"error": f"Invalid mode '{mode}'. Supported modes: driving, walking, cycling."}), 400

    result = nav_service.get_route(src, dst, mode)


    return jsonify(result), 200 if result.get("success") else 400


@nav_bp.route("/api/route/alternatives", methods=["POST"])
def calculate_alternatives():
    """
    Compare multiple candidate route alternatives using OSRM alternatives API.
    Request body: { "src": [28.6129, 77.2295], "dst": [28.6315, 77.2167], "mode": "driving" }
    """
    payload = request.get_json(force=True, silent=True) or {}
    src = payload.get("src")
    dst = payload.get("dst")
    mode = payload.get("mode", "driving")

    if not src or not dst:
        return jsonify({"error": "Fields 'src' and 'dst' are required."}), 400

    result = nav_service.get_route_alternatives(src, dst, mode)
    return jsonify(result), 200 if result.get("success") else 400


@nav_bp.route("/api/route/recommend", methods=["POST"])
def recommend_route():
    """
    Rank candidate routes based on user preference:
    - 'fastest_time'
    - 'shortest_distance'
    - 'minimal_detour'
    Request body: { "src": "India Gate", "dst": "Connaught Place", "preference": "fastest_time", "mode": "driving" }
    """
    payload = request.get_json(force=True, silent=True) or {}
    src = payload.get("src")
    dst = payload.get("dst")
    preference = payload.get("preference", "fastest_time")
    mode = payload.get("mode", "driving")

    if not src or not dst:
        return jsonify({"error": "Fields 'src' and 'dst' are required."}), 400

    result = recommender.compare_and_rank(src, dst, preference=preference, mode=mode)
    return jsonify(result), 200 if result.get("success") else 400


@nav_bp.route("/api/nearby", methods=["GET"])
def get_nearby_amenities():
    """
    Query Overpass API for nearby mapped places around coordinates.
    Query params:
    ?lat=28.6129&lon=77.2295&category=police&radius=2000
    (Accepts both 'category' and 'type' for amenity category)
    """
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (ValueError, TypeError, KeyError):
        return jsonify({"error": "Valid floating point 'lat' and 'lon' parameters are required."}), 400

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify({"error": "Latitude must be between -90 and 90, longitude between -180 and 180."}), 400

    amenity_type = (request.args.get("category") or request.args.get("type") or "police").strip().lower()

    try:
        radius = int(request.args.get("radius", 2000))
    except (ValueError, TypeError):
        radius = 2000

    pois = nav_service.get_nearby_pois(lat, lon, amenity_type=amenity_type, radius=radius)
    return jsonify(pois)

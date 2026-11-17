"""
Smart Campus Map Navigator - Flask Application Entry Point
Loads configuration, registers modular blueprints, enables CORS, and runs the server.
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from routes.location_routes import location_bp
from routes.graph_routes import graph_bp
from routes.navigation_routes import nav_bp
from routes.dsa_routes import dsa_bp
from routes.history_routes import history_bp


def create_app(config_class=Config) -> Flask:
    """Application factory for Smart Campus Map Navigator."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.config.from_object(config_class)

    # Enable Cross-Origin Resource Sharing (CORS) for Leaflet frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(location_bp)
    app.register_blueprint(graph_bp)
    app.register_blueprint(nav_bp)
    app.register_blueprint(dsa_bp)
    app.register_blueprint(history_bp)

    # ---------------------------------------------------------
    # Core Health & Information Endpoints
    # ---------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "OK",
            "service": "Smart Real-World Map Navigator Backend",
            "version": "2.0.0",
            "geocoder": "Photon API (OpenStreetMap / Komoot)",
            "routing_engine": "Open Source Routing Machine (OSRM)",
            "poi_service": "OpenStreetMap Overpass API (Cached)",
            "dsa_engine": "Manual Pure Python (BTITC305 Syllabus - No heapq/deque built-ins)"
        })

    # Serve Modern Frontend (or fallback to embedded UI if directory missing)
    @app.route("/", methods=["GET"])
    def index():
        # Always serve the modern frontend from the frontend directory
        return send_from_directory(frontend_dir, "index.html")

    # ---------------------------------------------------------
    # Error Handlers
    # ---------------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found", "status_code": 404}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "status_code": 400}), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error", "status_code": 500}), 500

    # Return a proper 404 for unknown API paths, rather than allowing the
    # frontend static-file catch-all to respond with 405 for POST/other methods.
    @app.route("/api/<path:unknown_api_path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    def unknown_api_endpoint(unknown_api_path):
        return jsonify({"error": "API endpoint not found", "status_code": 404}), 404

    # Serve any static file (CSS, JS, images) from the frontend directory
    @app.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory(frontend_dir, filename)

    return app


# Standalone Leaflet + DSA Testing Dashboard

app = create_app()

if __name__ == "__main__":
    print(f"Starting Smart Campus Map Navigator on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)


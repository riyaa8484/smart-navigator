"""
Navigation & Real-World GIS Integration Module
Integrates:
- Photon Geocoding API (Komoot / OpenStreetMap) for search-as-you-type and reverse geocoding
- Open Source Routing Machine (OSRM) for real road-following routing, turn-by-turn steps, and alternatives
- Overpass API (OpenStreetMap) for displaying nearby mapped places
- Educational Campus Graph router as an offline/testing fallback (preserving BTITC305 graph concepts)
"""

import math
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from config import Config
from graph import CampusGraph


class CacheWithTTL:
    """Thread-safe in-memory cache with TTL for API requests."""

    def __init__(self, default_ttl_seconds: int = 1800):
        self.default_ttl = default_ttl_seconds
        self.cache: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            timestamp, data = self.cache[key]
            if time.time() - timestamp < self.default_ttl:
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key: str, data: Any) -> None:
        self.cache[key] = (time.time(), data)


class NavigationService:
    """
    Orchestrates real-world geocoding, routing, and nearby-place queries.
    Uses free and open-source GIS services: Photon, OSRM, and Overpass API for nearby-place discovery.
    """

    USER_AGENT = "SmartMapNavigator/2.0 (Academic Project; NSUT BTITC305)"

    def __init__(self, campus_graph: Optional[CampusGraph] = None):
        self.graph = campus_graph or CampusGraph.load_from_json(Config.CAMPUS_DATA_FILE)
        self.cache = CacheWithTTL(Config.CACHE_TTL_SECONDS)
        self.last_overpass_request_time = 0.0
        self.last_overpass_error = None
        self.last_osrm_request_time = 0.0

    def _respect_osrm_rate_limit(self) -> None:
        """Keep requests to the public FOSSGIS demo router at or below 1/sec."""
        elapsed = time.time() - self.last_osrm_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self.last_osrm_request_time = time.time()

    @staticmethod
    def _osrm_base_for_profile(profile: str) -> str:
        """Return the OSRM host that is preprocessed for the requested mode.

        OSRM chooses its routing graph at server startup, not from the profile
        word in an arbitrary request path. FOSSGIS exposes separate routed-car,
        routed-foot and routed-bike prefixes, so each mode must use its own URL.
        """
        normalized = (profile or "driving").strip().lower()
        if normalized in ("foot", "walking", "walk"):
            return Config.OSRM_FOOT_BASE_URL
        if normalized in ("bike", "bicycle", "cycling", "cycle"):
            return Config.OSRM_BIKE_BASE_URL
        return Config.OSRM_CAR_BASE_URL

    # -------------------------------------------------------------
    # 1. Geometrical & Distance Calculations
    # -------------------------------------------------------------
    @staticmethod
    def haversine_distance(coord1: List[float], coord2: List[float]) -> float:
        """
        Calculate great-circle distance between two [lat, lon] points in kilometers.
        Uses Haversine formula:
        a = sin²(Δφ/2) + cos(φ1)⋅cos(φ2)⋅sin²(Δλ/2)
        c = 2⋅atan2(√a, √(1−a))
        d = R⋅c
        """
        lat1, lon1 = float(coord1[0]), float(coord1[1])
        lat2, lon2 = float(coord2[0]), float(coord2[1])
        R = 6371.0  # Earth's mean radius in km

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def resolve_coordinates(self, location_spec: Any) -> Optional[Tuple[float, float, str]]:
        """
        Resolves location specification to (lat, lon, label).
        Supports:
        - [lat, lon] or (lat, lon) list/tuple
        - {"lat": ..., "lon": ...} or {"coords": [lat, lon]}
        - Campus node code or name from campus graph
        - Address or place name string (via Photon geocoder)
        """
        if location_spec is None:
            return None

        # 1. Numeric coordinate pair [lat, lon]
        if isinstance(location_spec, (list, tuple)) and len(location_spec) == 2:
            try:
                lat = float(location_spec[0])
                lon = float(location_spec[1])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon, f"Location ({lat:.4f}, {lon:.4f})"
            except (ValueError, TypeError):
                pass

        # 2. Dictionary with lat/lon or coords
        if isinstance(location_spec, dict):
            if "lat" in location_spec and "lon" in location_spec:
                try:
                    lat = float(location_spec["lat"])
                    lon = float(location_spec["lon"])
                    name = location_spec.get("name") or f"Location ({lat:.4f}, {lon:.4f})"
                    return lat, lon, name
                except (ValueError, TypeError):
                    pass
            if "coords" in location_spec and isinstance(location_spec["coords"], (list, tuple)):
                return self.resolve_coordinates(location_spec["coords"])

        # 3. String identifier
        if isinstance(location_spec, str):
            clean_str = location_spec.strip()
            # Try comma-separated "lat, lon"
            if "," in clean_str:
                parts = clean_str.split(",")
                if len(parts) == 2:
                    try:
                        lat = float(parts[0].strip())
                        lon = float(parts[1].strip())
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            return lat, lon, f"Location ({lat:.4f}, {lon:.4f})"
                    except ValueError:
                        pass

            # Check campus node code (educational fallback)
            if clean_str in self.graph.nodes:
                node = self.graph.nodes[clean_str]
                coords = node.get("coords", [0, 0])
                return float(coords[0]), float(coords[1]), node.get("name", clean_str)

            # Check campus node name match
            for code, node in self.graph.nodes.items():
                if node.get("name", "").lower() == clean_str.lower() or code.lower() == clean_str.lower():
                    coords = node.get("coords", [0, 0])
                    return float(coords[0]), float(coords[1]), node.get("name", code)

            # Resolve location string via Photon geocoding
            search_results = self.search_locations(clean_str, limit=1)
            if search_results:
                best = search_results[0]
                return float(best["lat"]), float(best["lon"]), best["name"]

        return None

    # -------------------------------------------------------------
    # 2. Real Location Search (Photon API)
    # -------------------------------------------------------------
    def search_locations(self, query: str, limit: int = 10,
                         lat: Optional[float] = None, lon: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Real-world location search using Photon API (OpenStreetMap-based geocoding by Komoot).
        Supports search-as-you-type, place names, landmarks, addresses, and street intersections.
        Returns a list of multiple matching suggestions with detailed context.
        """
        query = (query or "").strip()
        if not query:
            return []

        normalized_query = " ".join(query.casefold().replace(",", " ").split())
        search_aliases = {
            "nsut": "Netaji Subhas University of Technology, Dwarka, New Delhi, India",
            "nsut dwarka": "Netaji Subhas University of Technology, Dwarka, New Delhi, India",
            "nsut delhi": "Netaji Subhas University of Technology, Dwarka, New Delhi, India",
            "nsit": "Netaji Subhas University of Technology, Dwarka, New Delhi, India"
        }
        query = search_aliases.get(normalized_query, query)

        cache_key = f"photon_search_{query.lower()}_{limit}_{lat}_{lon}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        results: List[Dict[str, Any]] = []

        # 1. Include matching campus locations (for academic demo context)
        for code, node in self.graph.nodes.items():
            name = node.get("name", "")
            cat = node.get("category", "")
            desc = node.get("description", "")
            if query.lower() in name.lower() or query.lower() in code.lower() or query.lower() in desc.lower():
                coords = node.get("coords", [0, 0])
                results.append({
                    "name": name,
                    "display_name": f"{name} (Campus {cat.capitalize()}, NSUT)",
                    "lat": float(coords[0]),
                    "lon": float(coords[1]),
                    "category": f"campus_{cat}",
                    "type": "campus_facility",
                    "city": "New Delhi",
                    "state": "Delhi",
                    "country": "India",
                    "source": "Campus Directory"
                })

        # 2. Query Photon API
        url = f"{Config.PHOTON_URL}/api/"
        params: Dict[str, Any] = {
            "q": query,
            "limit": limit
        }
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon

        try:
            resp = requests.get(
                url,
                params=params,
                headers={"User-Agent": self.USER_AGENT},
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                for feat in features:
                    props = feat.get("properties", {})
                    geom = feat.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])  # [lon, lat]

                    name = props.get("name") or props.get("street") or query.title()
                    # Build rich address context
                    parts = []
                    if props.get("name"):
                        parts.append(props["name"])
                    if props.get("housenumber") and props.get("street"):
                        parts.append(f"{props['housenumber']} {props['street']}")
                    elif props.get("street"):
                        parts.append(props["street"])
                    if props.get("district"):
                        parts.append(props["district"])
                    if props.get("city"):
                        parts.append(props["city"])
                    elif props.get("town"):
                        parts.append(props["town"])
                    if props.get("state"):
                        parts.append(props["state"])
                    if props.get("postcode"):
                        parts.append(str(props["postcode"]))
                    if props.get("country"):
                        parts.append(props["country"])

                    display_name = ", ".join(parts) if parts else name

                    results.append({
                        "name": name,
                        "display_name": display_name,
                        "lat": coords[1],
                        "lon": coords[0],
                        "category": props.get("osm_value") or props.get("osm_key") or props.get("type", "place"),
                        "type": props.get("type", "feature"),
                        "osm_type": props.get("osm_type"),
                        "osm_id": props.get("osm_id"),
                        "street": props.get("street"),
                        "city": props.get("city") or props.get("town"),
                        "state": props.get("state"),
                        "postcode": props.get("postcode"),
                        "country": props.get("country"),
                        "source": "OpenStreetMap / Photon"
                    })
        except Exception:
            # If network error, campus matches (if any) are returned
            pass

        self.cache.set(cache_key, results)
        return results

    def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Reverse geocoding using Photon API: converts (lat, lon) to place name and address.
        """
        cache_key = f"photon_rev_{round(lat, 5)}_{round(lon, 5)}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{Config.PHOTON_URL}/reverse"
        params = {"lat": lat, "lon": lon}

        try:
            resp = requests.get(
                url,
                params=params,
                headers={"User-Agent": self.USER_AGENT},
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                if features:
                    props = features[0].get("properties", {})
                    name = props.get("name") or props.get("street") or f"Location ({lat:.4f}, {lon:.4f})"
                    parts = [p for p in [props.get("street"), props.get("city"), props.get("state"), props.get("country")] if p]
                    res = {
                        "success": True,
                        "name": name,
                        "formatted_address": ", ".join(parts) if parts else name,
                        "lat": lat,
                        "lon": lon,
                        "details": props
                    }
                    self.cache.set(cache_key, res)
                    return res
        except Exception:
            pass

        return {
            "success": True,
            "name": f"Location ({lat:.4f}, {lon:.4f})",
            "formatted_address": f"Latitude: {lat:.5f}, Longitude: {lon:.5f}",
            "lat": lat,
            "lon": lon,
            "offline_fallback": True
        }

    # -------------------------------------------------------------
    # 3. Real Road Routing via OSRM
    # -------------------------------------------------------------
    def get_route(self, src: Any, dst: Any, mode: str = "driving", alternatives: bool = False) -> Dict[str, Any]:
        """
        Calculate actual road-following route between source and destination using OSRM.
        Retrieves real road geometry, step-by-step turn instructions, road names, and metrics.
        """
        src_resolved = self.resolve_coordinates(src)
        dst_resolved = self.resolve_coordinates(dst)

        if not src_resolved or not dst_resolved:
            return {
                "success": False,
                "error": "Could not resolve source or destination coordinates.",
                "src": src,
                "dst": dst
            }

        src_lat, src_lon, src_name = src_resolved
        dst_lat, dst_lon, dst_name = dst_resolved

        # Map mode to valid OSRM profile
        # Public OSRM server supports 'driving', 'foot', and 'bike'
        mode_lower = (mode or "driving").lower().strip()
        if mode_lower in ("walking", "walk", "foot"):
            profile = "foot"
            transport_mode = "walking"
        elif mode_lower in ("cycling", "bicycle", "bike"):
            profile = "bike"
            transport_mode = "cycling"
        else:
            profile = "driving"
            transport_mode = "driving"

        # Attempt real OSRM routing
        osrm_result = self._query_osrm(src_lon, src_lat, dst_lon, dst_lat, profile, alternatives=alternatives)
        if osrm_result.get("success"):
            osrm_result["src_name"] = src_name
            osrm_result["dst_name"] = dst_name
            osrm_result["src_coords"] = [src_lat, src_lon]
            osrm_result["dst_coords"] = [dst_lat, dst_lon]
            osrm_result["mode"] = transport_mode
            return osrm_result

        # Honest fallback: Educational Campus Graph / simulated offline path
        # NEVER claim an offline fallback is real road navigation!
        return self._fallback_route(src_lat, src_lon, dst_lat, dst_lon, src_name, dst_name, transport_mode, src, dst)

    def _query_osrm(self, start_lon: float, start_lat: float,
                    end_lon: float, end_lat: float, profile: str, alternatives: bool = False) -> Dict[str, Any]:
        """
        Queries OSRM Route API:
        /route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson&steps=true&alternatives={true/false}
        """
        coord_str = f"{start_lon:.6f},{start_lat:.6f};{end_lon:.6f},{end_lat:.6f}"
        alt_param = "true" if alternatives else "false"
        # The FOSSGIS endpoint prefix selects car/foot/bike. The OSRM path
        # profile segment is kept as "driving" for compatibility with that service.
        routing_base = self._osrm_base_for_profile(profile)
        url = f"{routing_base}/route/v1/driving/{coord_str}?overview=full&geometries=geojson&steps=true&alternatives={alt_param}"

        try:
            self._respect_osrm_rate_limit()
            resp = requests.get(url, headers={"User-Agent": self.USER_AGENT}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    routes = data["routes"]
                    primary = routes[0]

                    # Parse primary route
                    parsed_primary = self._parse_osrm_route(primary)

                    result: Dict[str, Any] = {
                        "success": True,
                        "source": "Open Source Routing Machine (OSRM)",
                        "is_real_routing": True,
                        "profile": profile,
                        "distance_km": parsed_primary["distance_km"],
                        "duration_min": parsed_primary["duration_min"],
                        "duration_s": parsed_primary["duration_s"],
                        "instructions": parsed_primary["instructions"],
                        "geojson": {
                            "type": "FeatureCollection",
                            "features": [{
                                "type": "Feature",
                                "properties": {
                                    "name": f"Route ({parsed_primary['distance_km']} km)",
                                    "distance_km": parsed_primary["distance_km"],
                                    "duration_min": parsed_primary["duration_min"],
                                    "profile": profile
                                },
                                "geometry": parsed_primary["geometry"]
                            }]
                        }
                    }

                    # If alternatives exist, parse them
                    if len(routes) > 1:
                        parsed_alts = []
                        for idx, r in enumerate(routes):
                            parsed = self._parse_osrm_route(r)
                            parsed_alts.append({
                                "id": idx + 1,
                                "name": "Fastest Route" if idx == 0 else f"Alternative Route {idx}",
                                "distance_km": parsed["distance_km"],
                                "duration_min": parsed["duration_min"],
                                "summary": f"Via {parsed['summary_road']}" if parsed["summary_road"] else f"Alternative {idx}",
                                "segments_count": len(parsed["instructions"]),
                                "geometry": parsed["geometry"]["coordinates"],
                                "instructions": parsed["instructions"]
                            })
                        result["alternatives"] = parsed_alts

                    return result
        except Exception:
            pass

        return {"success": False}

    def _parse_osrm_route(self, route_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Parses an individual OSRM route object extracting metrics, geometry, and instructions."""
        distance_m = route_obj.get("distance", 0.0)
        duration_s = route_obj.get("duration", 0.0)

        distance_km = round(distance_m / 1000.0, 3)
        duration_min = round(duration_s / 60.0, 1)

        instructions: List[Dict[str, Any]] = []
        road_names_encountered: List[str] = []

        legs = route_obj.get("legs", [])
        step_idx = 1
        for leg in legs:
            steps = leg.get("steps", [])
            for s in steps:
                maneuver = s.get("maneuver", {})
                m_type = maneuver.get("type", "continue")
                m_modifier = maneuver.get("modifier", "")
                road_name = s.get("name", "").strip()
                step_dist_m = round(s.get("distance", 0.0), 1)
                step_dur_s = round(s.get("duration", 0.0), 1)
                location = maneuver.get("location", [])

                if road_name and road_name not in road_names_encountered:
                    road_names_encountered.append(road_name)

                instruction_text = self._format_osrm_instruction(m_type, m_modifier, road_name, maneuver)

                instructions.append({
                    "step_number": step_idx,
                    "instruction": instruction_text,
                    "road_name": road_name or "Unnamed Road",
                    "manoeuvre_type": m_type,
                    "manoeuvre_modifier": m_modifier,
                    "distance_m": step_dist_m,
                    "duration_s": step_dur_s,
                    "location": location
                })
                step_idx += 1

        summary_road = road_names_encountered[0] if road_names_encountered else ""

        return {
            "distance_km": distance_km,
            "duration_min": max(0.5, duration_min),
            "duration_s": round(duration_s, 1),
            "instructions": instructions,
            "geometry": route_obj.get("geometry", {}),
            "summary_road": summary_road
        }

    @staticmethod
    def _format_osrm_instruction(m_type: str, modifier: str, road_name: str, maneuver: Dict[str, Any]) -> str:
        """Formats an OSRM step maneuver into clear, human-readable turn-by-turn instruction."""
        modifier_clean = modifier.replace("_", " ").title() if modifier else ""
        road_str = f" onto {road_name}" if road_name else ""

        if m_type == "depart":
            return f"Head {modifier_clean.lower() or 'forward'} on {road_name or 'the road'}"
        elif m_type == "arrive":
            side_str = f" on your {modifier_clean.lower()}" if modifier_clean else ""
            return f"Arrive at your destination{side_str}"
        elif m_type == "turn":
            return f"Turn {modifier_clean.lower()}{road_str}"
        elif m_type == "new name":
            return f"Continue onto {road_name}" if road_name else "Continue along the road"
        elif m_type == "continue":
            return f"Continue straight{road_str}"
        elif m_type in ("roundabout", "rotary"):
            exit_num = maneuver.get("exit")
            exit_str = f" and take exit {exit_num}" if exit_num else ""
            return f"Enter roundabout{exit_str}{road_str}"
        elif m_type == "fork":
            return f"Take the {modifier_clean.lower()} fork{road_str}"
        elif m_type == "merge":
            return f"Merge {modifier_clean.lower()}{road_str}"
        elif m_type == "end of road":
            return f"At the end of the road, turn {modifier_clean.lower()}{road_str}"
        elif m_type in ("on ramp", "off ramp"):
            return f"Take the {m_type}{road_str}"
        else:
            action = m_type.replace("_", " ").title()
            mod = f" {modifier_clean.lower()}" if modifier_clean else ""
            return f"{action}{mod}{road_str}".strip()

    # -------------------------------------------------------------
    # 4. Route Alternatives
    # -------------------------------------------------------------
    def get_route_alternatives(self, src: Any, dst: Any, mode: str = "driving") -> Dict[str, Any]:
        """
        Request genuine alternative routes from OSRM (alternatives=true).
        When falling back to the educational campus graph, computes the 2nd alternative
        path through the graph structure (Yen's K-shortest path approach).
        """
        full_res = self.get_route(src, dst, mode=mode, alternatives=True)
        if not full_res.get("success"):
            return full_res

        alts = full_res.get("alternatives", [])
        if not alts:
            alts = [{
                "id": 1,
                "name": "Fastest Route (Primary)",
                "distance_km": full_res.get("distance_km"),
                "duration_min": full_res.get("duration_min"),
                "segments_count": len(full_res.get("instructions", [])),
                "summary": "Primary calculated route",
                "geometry": full_res.get("geojson", {}).get("features", [{}])[0].get("geometry", {}).get("coordinates", []),
                "instructions": full_res.get("instructions", [])
            }]

        # If only 1 route was returned (e.g. offline fallback on campus nodes),
        # compute an authentic second path through the campus graph
        if len(alts) == 1 and isinstance(src, str) and src in self.graph.nodes and isinstance(dst, str) and dst in self.graph.nodes:
            dijkstra_primary = self.graph.dijkstra_shortest_path(src, dst)
            primary_path = dijkstra_primary.get("path", [])
            if len(primary_path) >= 2:
                # Omit first edge to find alternative route
                u, v = primary_path[0], primary_path[1]
                orig_neighbors = list(self.graph.adj_list.get(u, []))
                self.graph.adj_list[u] = [(n, w) for (n, w) in orig_neighbors if n != v]
                alt_dijkstra = self.graph.dijkstra_shortest_path(src, dst)
                self.graph.adj_list[u] = orig_neighbors  # Restore

                if alt_dijkstra.get("found"):
                    alt_path = alt_dijkstra.get("path", [])
                    alt_coords: List[List[float]] = []
                    for code in alt_path:
                        c = self.graph.nodes[code].get("coords", [0, 0])
                        alt_coords.append([c[1], c[0]])
                    alt_dist = round(alt_dijkstra.get("distance", 0.0), 3)
                    speed_kmh = 4.5 if mode in ("walking", "walk") else 25.0
                    alt_dur = round((alt_dist / speed_kmh) * 60.0, 1)

                    alts.append({
                        "id": 2,
                        "name": f"Campus Alternative Path ({' → '.join(alt_path)})",
                        "distance_km": alt_dist,
                        "duration_min": max(1.0, alt_dur),
                        "segments_count": len(alt_path),
                        "summary": f"Via {' → '.join(alt_path[1:-1])}",
                        "geometry": alt_coords,
                        "instructions": [
                            {"step_number": i + 1, "instruction": f"Proceed via {node_code}", "road_name": node_code, "distance_m": 150, "duration_s": 60}
                            for i, node_code in enumerate(alt_path)
                        ]
                    })

        return {
            "success": True,
            "source": full_res.get("source"),
            "is_real_routing": full_res.get("is_real_routing", False),
            "src": src,
            "dst": dst,
            "mode": mode,
            "alternatives": alts
        }

    # -------------------------------------------------------------
    # 5. Nearby Places (Overpass API)
    # -------------------------------------------------------------
    def get_nearby_pois(self, lat: float, lon: float, amenity_type: str = "police",
                        radius: int = 2000) -> List[Dict[str, Any]]:
        """Return real OSM amenities (nodes, ways and relations) near a point.

        Multiple public Overpass instances are tried in sequence. The server-side
        query timeout is deliberately shorter than the HTTP read timeout so the
        client does not abandon a query while the Overpass server is still working.
        """
        amenity_type = (amenity_type or "police").strip().lower()
        radius = max(200, min(int(radius), 15000))
        cache_key = f"overpass_{round(lat, 4)}_{round(lon, 4)}_{amenity_type}_{radius}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        self.last_overpass_error = None
        elapsed = time.time() - self.last_overpass_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self.last_overpass_request_time = time.time()

        osm_filter = self._build_overpass_filter(amenity_type, radius, lat, lon)
        overpass_query = f"""
        [out:json][timeout:25];
        (
          {osm_filter}
        );
        out center tags;
        """

        pois: List[Dict[str, Any]] = []
        endpoints = [
            Config.OVERPASS_URL,
            Config.OVERPASS_BACKUP_URL,
            getattr(Config, "OVERPASS_FALLBACK_URL", "https://overpass-api.de/api/interpreter"),
        ]
        seen_ids = set()

        for endpoint in endpoints:
            try:
                resp = requests.post(
                    endpoint,
                    data={"data": overpass_query},
                    headers={
                        "User-Agent": self.USER_AGENT,
                        "Accept": "application/json"
                    },
                    timeout=(6, 35)
                )

                if resp.status_code != 200:
                    self.last_overpass_error = f"{endpoint} returned HTTP {resp.status_code}"
                    continue

                data = resp.json()
                remark = data.get("remark")
                self.last_overpass_error = str(remark)[:300] if remark else None

                for el in data.get("elements", []):
                    tags = el.get("tags") or {}
                    el_lat = el.get("lat")
                    el_lon = el.get("lon")
                    if el_lat is None or el_lon is None:
                        center = el.get("center") or {}
                        el_lat = center.get("lat")
                        el_lon = center.get("lon")
                    if el_lat is None or el_lon is None:
                        continue

                    element_key = (el.get("type"), el.get("id"))
                    if element_key in seen_ids:
                        continue
                    seen_ids.add(element_key)

                    name = tags.get("name") or self._generate_amenity_name(tags, amenity_type)
                    distance = round(self.haversine_distance([lat, lon], [el_lat, el_lon]), 3)
                    addr_parts = [
                        tags.get("addr:housenumber"), tags.get("addr:street"),
                        tags.get("addr:suburb"), tags.get("addr:city")
                    ]
                    address = ", ".join(part for part in addr_parts if part) or tags.get("addr:full", "")
                    actual_type = (
                        tags.get("amenity") or tags.get("healthcare") or tags.get("shop")
                        or tags.get("railway") or tags.get("highway") or amenity_type
                    )

                    pois.append({
                        "type": "Feature",
                        "properties": {
                            "id": el.get("id"),
                            "osm_type": el.get("type"),
                            "name": name,
                            "amenity": actual_type,
                            "operator": tags.get("operator", ""),
                            "address": address or "Address not mapped in OpenStreetMap",
                            "phone": tags.get("phone", tags.get("contact:phone", "")),
                            "opening_hours": tags.get("opening_hours", "")
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [round(float(el_lon), 6), round(float(el_lat), 6)]
                        },
                        "distance": distance
                    })

                # Stop as soon as a provider returns real matches. If it returns
                # an empty result, try the next endpoint in case its data is fresher.
                if pois:
                    break

            except requests.Timeout:
                self.last_overpass_error = f"{endpoint} timed out while searching {amenity_type} facilities"
            except requests.RequestException as exc:
                self.last_overpass_error = f"{endpoint}: {exc.__class__.__name__}"
            except (ValueError, TypeError) as exc:
                self.last_overpass_error = f"{endpoint} returned an unreadable response: {exc.__class__.__name__}"
            except Exception as exc:
                self.last_overpass_error = f"{endpoint}: {exc.__class__.__name__}"

        pois.sort(key=lambda item: item.get("distance", float("inf")))
        # Cache only positive results. Do not invent facilities when OSM has none.
        if pois:
            self.cache.set(cache_key, pois)
        return pois

    @staticmethod
    def _build_overpass_filter(amenity_type: str, radius: int, lat: float, lon: float) -> str:
        """Build Overpass filters for nodes, ways and relations."""
        if amenity_type in ("police", "police_station"):
            return f'''nwr["amenity"="police"](around:{radius},{lat},{lon});'''
        if amenity_type in ("hospital", "clinic", "health"):
            return f'''nwr["amenity"="hospital"](around:{radius},{lat},{lon});
                       nwr["amenity"="clinic"](around:{radius},{lat},{lon});
                       nwr["healthcare"="hospital"](around:{radius},{lat},{lon});'''
        if amenity_type in ("pharmacy", "chemist", "medicine"):
            return f'''nwr["amenity"="pharmacy"](around:{radius},{lat},{lon});
                       nwr["healthcare"="pharmacy"](around:{radius},{lat},{lon});
                       nwr["shop"="chemist"](around:{radius},{lat},{lon});'''
        if amenity_type in ("fuel", "petrol_pump", "gas_station"):
            return f'''nwr["amenity"="fuel"](around:{radius},{lat},{lon});'''
        if amenity_type in ("atm", "bank"):
            return f'''nwr["amenity"="atm"](around:{radius},{lat},{lon});
                       nwr["amenity"="bank"](around:{radius},{lat},{lon});'''
        if amenity_type in ("metro_station", "metro", "subway"):
            return f'''nwr["railway"="station"]["station"="subway"](around:{radius},{lat},{lon});
                       nwr["railway"="subway_entrance"](around:{radius},{lat},{lon});'''
        if amenity_type in ("bus_stop", "bus_station"):
            return f'''nwr["highway"="bus_stop"](around:{radius},{lat},{lon});
                       nwr["amenity"="bus_station"](around:{radius},{lat},{lon});'''
        if amenity_type in ("restaurant", "food", "cafe"):
            return f'''nwr["amenity"="restaurant"](around:{radius},{lat},{lon});
                       nwr["amenity"="cafe"](around:{radius},{lat},{lon});'''
        if amenity_type == "parking":
            return f'''nwr["amenity"="parking"](around:{radius},{lat},{lon});'''
        return f'''nwr["amenity"="{amenity_type}"](around:{radius},{lat},{lon});'''

    @staticmethod
    def _generate_amenity_name(tags: Dict[str, Any], default_type: str) -> str:
        op = tags.get("operator")
        brand = tags.get("brand")
        prefix = brand or op
        if prefix:
            return f"{prefix} {default_type.replace('_', ' ').title()}"
        return f"{default_type.replace('_', ' ').title()}"

    # -------------------------------------------------------------
    # 6. Educational Fallback Router (Campus Graph)
    # -------------------------------------------------------------
    def _fallback_route(self, src_lat: float, src_lon: float, dst_lat: float, dst_lon: float,
                        src_name: str, dst_name: str, mode: str, orig_src: Any, orig_dst: Any) -> Dict[str, Any]:
        """
        Pure offline/campus fallback using internal graph or direct geometry.
        Transparently flags 'is_real_routing': False to maintain strict technical honesty.
        """
        node_path: List[str] = []
        if isinstance(orig_src, str) and orig_src in self.graph.nodes and \
           isinstance(orig_dst, str) and orig_dst in self.graph.nodes:
            dijkstra_res = self.graph.dijkstra_shortest_path(orig_src, orig_dst)
            if dijkstra_res.get("found"):
                node_path = dijkstra_res.get("path", [])

        coordinates: List[List[float]] = []
        total_dist_km = 0.0

        if len(node_path) > 1:
            for code in node_path:
                node_coords = self.graph.nodes[code].get("coords", [src_lat, src_lon])
                coordinates.append([node_coords[1], node_coords[0]])
            for i in range(len(coordinates) - 1):
                p1 = [coordinates[i][1], coordinates[i][0]]
                p2 = [coordinates[i + 1][1], coordinates[i + 1][0]]
                total_dist_km += self.haversine_distance(p1, p2)
        else:
            coordinates = [
                [src_lon, src_lat],
                [dst_lon, dst_lat]
            ]
            total_dist_km = self.haversine_distance([src_lat, src_lon], [dst_lat, dst_lon])

        speed_kmh = 4.5 if mode == "walking" else (15.0 if mode == "cycling" else 30.0)
        duration_min = round((total_dist_km / speed_kmh) * 60.0, 1)
        total_dist_km = round(total_dist_km, 3)

        instructions = [
            {"step_number": 1, "instruction": f"Depart from {src_name}", "road_name": src_name, "distance_m": 0, "duration_s": 0},
            {"step_number": 2, "instruction": f"Proceed towards destination: {dst_name}", "road_name": dst_name, "distance_m": round(total_dist_km * 1000, 0), "duration_s": round(duration_min * 60, 0)},
            {"step_number": 3, "instruction": f"Arrive at {dst_name}", "road_name": dst_name, "distance_m": 0, "duration_s": 0}
        ]

        return {
            "success": True,
            "source": "Campus Graph Router (Offline Fallback)",
            "is_real_routing": False,
            "disclaimer": "Offline routing fallback: coordinates are derived from campus graph or straight geometry. Set up network access to OSRM for road navigation.",
            "src_name": src_name,
            "dst_name": dst_name,
            "mode": mode,
            "distance_km": total_dist_km,
            "duration_min": max(1.0, duration_min),
            "instructions": instructions,
            "node_path": node_path,
            "geojson": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "name": f"Route from {src_name} to {dst_name}",
                        "distance_km": total_dist_km,
                        "duration_min": duration_min
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates
                    }
                }]
            }
        }

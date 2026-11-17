"""
Recommendation & Route Ranking Module
Evaluates multiple candidate routes based on user preferences:
- shortest distance
- fastest time
- minimal detour
Ranks routes and returns justification/explanation of recommendation.
"""

from typing import List, Dict, Any
from navigation import NavigationService


class RouteRecommender:
    """Ranks and scores route candidates according to user preferences."""

    def __init__(self, nav_service: NavigationService):
        self.nav = nav_service

    def compare_and_rank(self, src: Any, dst: Any, preference: str = "fastest_time",
                         mode: str = "driving") -> Dict[str, Any]:
        """
        Evaluate and rank the direct route and available road-route alternatives.
        Returns ranked candidate list with scoring breakdown and human-readable explanation.
        """
        candidates: List[Dict[str, Any]] = []

        # 1. Direct standard route
        primary = self.nav.get_route(src, dst, mode)
        if primary.get("success"):
            candidates.append({
                "id": "direct_shortest",
                "label": "Direct Shortest Distance Route",
                "distance_km": primary.get("distance_km"),
                "duration_min": primary.get("duration_min"),
                "route_data": primary,
                "detour_km": 0.0
            })

        # 2. Alternative routes
        alts = self.nav.get_route_alternatives(src, dst, mode)
        if alts.get("success"):
            for alt in alts.get("alternatives", []):
                if alt.get("id") != 1:  # avoid exact duplicate of primary
                    candidates.append({
                        "id": f"alt_{alt.get('id')}",
                        "label": alt.get("name"),
                        "distance_km": alt.get("distance_km"),
                        "duration_min": alt.get("duration_min"),
                        "summary": alt.get("summary"),
                        "detour_km": round(alt.get("distance_km", 0) - primary.get("distance_km", 0), 2)
                    })

        if not candidates:
            return {"success": False, "error": "No viable routes could be calculated."}

        # Scoring candidates
        # Normalized min distance and min duration across candidates
        min_dist = min(c["distance_km"] for c in candidates)
        min_dur = min(c["duration_min"] for c in candidates)

        for c in candidates:
            dist_score = (min_dist / c["distance_km"]) * 50 if c["distance_km"] > 0 else 50
            time_score = (min_dur / c["duration_min"]) * 50 if c["duration_min"] > 0 else 50
            # Weighting based on preference
            pref_lower = preference.lower()
            if "distance" in pref_lower or "shortest" in pref_lower:
                total_score = dist_score * 1.5 + time_score * 0.5
            elif "detour" in pref_lower:
                detour_penalty = c.get("detour_km", 0.0) * 10
                total_score = dist_score + time_score - detour_penalty
            else:  # default fastest_time
                total_score = time_score * 1.5 + dist_score * 0.5

            c["score"] = round(total_score, 2)

        # Sort descending by score
        candidates.sort(key=lambda x: x["score"], reverse=True)
        winner = candidates[0]

        # Formulate rationale
        explanation = (
            f"Candidate '{winner['label']}' was ranked highest with a score of {winner['score']}. "
            f"It covers {winner['distance_km']} km in ~{winner['duration_min']} minutes. "
            f"Selection prioritised user preference for '{preference}'."
        )

        return {
            "success": True,
            "preference": preference,
            "ranked_routes": candidates,
            "top_choice": winner,
            "explanation": explanation
        }


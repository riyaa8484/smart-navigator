"""
Unit Tests for Smart Campus Map Navigator Flask API Endpoints.
Verifies health, locations CRUD, graph endpoints, road routing, nearby-place search, and DSA APIs.
"""

import unittest
import json
from app import create_app


class TestNavigatorAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "OK")

    def test_locations_endpoints(self):
        # 1. Get locations
        res = self.client.get("/api/locations")
        self.assertEqual(res.status_code, 200)
        locs = res.get_json()
        self.assertTrue(len(locs) > 0)

        # 2. Search
        search_res = self.client.get("/api/locations/search?q=Library")
        self.assertEqual(search_res.status_code, 200)
        search_data = search_res.get_json()
        self.assertTrue(any("library" in l["name"].lower() for l in search_data))

        # 3. Add location
        new_loc_payload = {
            "name": "Botanical Garden",
            "coords": [28.6925, 77.1210],
            "category": "nature"
        }
        post_res = self.client.post("/api/locations", json=new_loc_payload)
        self.assertEqual(post_res.status_code, 201)
        created_id = post_res.get_json()["location"]["id"]

        # 4. Delete location
        del_res = self.client.delete(f"/api/locations/{created_id}")
        self.assertEqual(del_res.status_code, 200)

    def test_optional_facility_detour_endpoint_removed(self):
        res = self.client.post("/api/route/via-facility", json={
            "src": "India Gate", "dst": "NSUT", "facility": "pharmacy"
        })
        self.assertEqual(res.status_code, 404)

    def test_graph_endpoints(self):
        # Adjacency list & matrix
        res_list = self.client.get("/api/graph/adjacency-list")
        self.assertEqual(res_list.status_code, 200)

        res_mat = self.client.get("/api/graph/adjacency-matrix")
        self.assertEqual(res_mat.status_code, 200)

        # BFS
        bfs_res = self.client.post("/api/graph/bfs", json={"start": "MainGate", "end": "Library"})
        self.assertEqual(bfs_res.status_code, 200)
        self.assertTrue(bfs_res.get_json()["found"])

        # DFS
        dfs_res = self.client.post("/api/graph/dfs", json={"start": "MainGate", "end": "Library"})
        self.assertEqual(dfs_res.status_code, 200)
        self.assertTrue(dfs_res.get_json()["found"])

        # MST
        prim_res = self.client.get("/api/graph/mst/prim")
        self.assertEqual(prim_res.status_code, 200)
        kruskal_res = self.client.get("/api/graph/mst/kruskal")
        self.assertEqual(kruskal_res.status_code, 200)

    def test_routing_endpoints(self):
        # Route
        route_res = self.client.post("/api/route", json={
            "src": "MainGate",
            "dst": "Library",
            "mode": "driving"
        })
        self.assertEqual(route_res.status_code, 200)
        data = route_res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("geojson", data)

        # Alternatives
        alt_res = self.client.post("/api/route/alternatives", json={
            "src": "MainGate",
            "dst": "Library"
        })
        self.assertEqual(alt_res.status_code, 200)
        self.assertTrue(len(alt_res.get_json()["alternatives"]) >= 2)

        # Nearby POI
        nearby_res = self.client.get("/api/nearby?lat=28.6885&lon=77.1200&type=hospital")
        self.assertEqual(nearby_res.status_code, 200)
        pois = nearby_res.get_json()
        self.assertTrue(isinstance(pois, list))

        # Real-world Place Search (Photon API endpoint)
        search_res = self.client.get("/api/search?q=Library")
        self.assertEqual(search_res.status_code, 200)
        search_data = search_res.get_json()
        self.assertTrue(search_data.get("success"))
        self.assertIn("results", search_data)

        # Search validation error
        empty_search = self.client.get("/api/search")
        self.assertEqual(empty_search.status_code, 400)

        # Reverse Geocode
        rev_res = self.client.get("/api/reverse-geocode?lat=28.6129&lon=77.2295")
        self.assertEqual(rev_res.status_code, 200)

        # Route validation: missing parameters
        bad_route = self.client.post("/api/route", json={"src": "MainGate"})
        self.assertEqual(bad_route.status_code, 400)

    def test_dsa_lab_endpoints(self):
        # Stack
        stack_res = self.client.post("/api/dsa/stack", json={"expr": "(A+B)*C"})
        self.assertEqual(stack_res.status_code, 200)
        self.assertEqual(stack_res.get_json()["postfix"], "AB+C*")

        # Queue
        queue_res = self.client.post("/api/dsa/queue", json={"items": [1, 2, 3]})
        self.assertEqual(queue_res.status_code, 200)
        self.assertEqual(queue_res.get_json()["processed"], [1, 2, 3])

        # Circular Queue
        cq_res = self.client.post("/api/dsa/circular-queue", json={"capacity": 5, "items": [1, 2, 3, 4]})
        self.assertEqual(cq_res.status_code, 200)

        # Priority Queue
        pq_res = self.client.post("/api/dsa/priority-queue", json={"items": [{"val": "A", "pri": 1}, {"val": "B", "pri": 0}]})
        self.assertEqual(pq_res.status_code, 200)

        # Linked List
        ll_res = self.client.post("/api/dsa/linked-list", json={"list": [1, 2, 3], "op": "reverse"})
        self.assertEqual(ll_res.status_code, 200)
        self.assertEqual(ll_res.get_json()["reversed"], [3, 2, 1])

        # Trees
        tree_res = self.client.post("/api/dsa/trees", json={"values": [30, 20, 40]})
        self.assertEqual(tree_res.status_code, 200)
        self.assertEqual(tree_res.get_json()["inorder"], [20, 30, 40])

        # Hashing
        hash_res = self.client.post("/api/dsa/hashing", json={"keys": ["alpha", "beta"]})
        self.assertEqual(hash_res.status_code, 200)

        # Heaps
        heap_res = self.client.post("/api/dsa/heaps", json={"values": [5, 1, 9, 3]})
        self.assertEqual(heap_res.status_code, 200)
        self.assertEqual(heap_res.get_json()["min_heap_root"], 1)

        # Search
        search_res = self.client.post("/api/dsa/search", json={"list": [10, 20, 30, 40], "target": 30, "method": "binary"})
        self.assertEqual(search_res.status_code, 200)
        self.assertTrue(search_res.get_json()["found"])

        # Sort
        sort_res = self.client.post("/api/dsa/sort", json={"list": [4, 2, 5, 1, 3], "algorithm": "quick"})
        self.assertEqual(sort_res.status_code, 200)
        self.assertEqual(sort_res.get_json()["sorted"], [1, 2, 3, 4, 5])

        # Complexity
        comp_res = self.client.get("/api/dsa/complexity?algorithm=bfs")
        self.assertEqual(comp_res.status_code, 200)
        self.assertEqual(comp_res.get_json()["name"], "Breadth-First Search")

    def test_history_endpoints(self):
        # Post history
        add_res = self.client.post("/api/history", json={"src": "MainGate", "dst": "Library"})
        self.assertEqual(add_res.status_code, 201)

        # Get history
        get_res = self.client.get("/api/history")
        self.assertEqual(get_res.status_code, 200)
        self.assertTrue(len(get_res.get_json()) > 0)

        # Back & Forward
        self.client.post("/api/history", json={"src": "Library", "dst": "CSDepartment"})
        back_res = self.client.post("/api/history/back")
        self.assertEqual(back_res.status_code, 200)
        forward_res = self.client.post("/api/history/forward")
        self.assertEqual(forward_res.status_code, 200)

        # Undo
        undo_res = self.client.post("/api/history/undo")
        self.assertEqual(undo_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()


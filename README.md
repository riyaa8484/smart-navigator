# Smart Navigator

A real-world map navigation application built with **Python, Flask, JavaScript, Leaflet, and OpenStreetMap**. It searches for places, calculates road routes, shows route alternatives and turn-by-turn directions, explores nearby mapped places, and keeps a route history.

## Main features

- Search and autocomplete for real places and addresses using Photon.
- Reverse geocoding: convert map coordinates into a readable place name.
- Drive, Walk, and Bike routing using profile-specific OSRM services.
- Alternative routes, route-priority recommendations, distance/time summary, and turn-by-turn steps.
- Explore Nearby using OpenStreetMap Overpass. Nearby-place exploration is separate from route calculation.
- Origin and destination markers, map-click location selection, and location swapping.
- Automatic JSON-backed History with Back, Forward, Undo, and Delete controls.
- Flask API blueprints for navigation, campus locations, graph algorithms, History, and DSA demonstrations.
- Default premium dark charcoal / dusty-rose interface with a cloudy-night map style.

Facility waypoint detours and the unfinished Saved Routes feature are intentionally not included.

## How the application works

```text
Browser (HTML + CSS + JavaScript)
          |
          v
Frontend components + ApiService (fetch / JSON)
          |
          v
Flask app.py (registers API blueprints)
          |
          +--> NavigationService --> Photon / OSRM / Overpass
          |
          +--> CampusGraph --> BFS / DFS / Dijkstra / MST fallback and demos
          |
          +--> HistoryManager --> ArrayStack + JSON route records
          |
          +--> DSA modules --> arrays, stacks, queues, lists, trees, hashing, heaps,
                               searching, sorting, graphs, complexity
```

## Project structure

```text
Smart_Navigator/
├── app.py                     # Creates the Flask app and registers blueprints
├── config.py                  # Environment settings and API URLs
├── requirements.txt           # Flask, CORS, requests, Gunicorn
├── campus_data.json           # Sample campus nodes and graph data
├── history_data.json          # Created automatically when the first route is saved
├── routes/                    # Navigation, History, graph, location, and DSA APIs
├── frontend/                  # HTML, JavaScript components, and CSS themes
├── tests/                     # API and DSA tests
└── *.py                       # Navigation, graph, History, and DSA implementations
```

## Run locally (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open **http://127.0.0.1:5000**. Network access is needed for live place search, road routing, and nearby-place search.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

The project contains API tests and DSA tests. The local working copy was verified by the user with **29/29 tests passing** after the final frontend repair. To run only the data-structure tests:

```powershell
python -m unittest tests.test_dsa -v
```

## Deployment on Render

Create a **Python Web Service** from the project repository and use:

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| Environment variable | `FLASK_DEBUG=False` |
| Health-check path (optional) | `/api/health` |

The app serves its own frontend, so one Flask web service is sufficient. Do not deploy it as a static site.

### Important History limitation

History is written to `history_data.json`. Render's default filesystem is ephemeral: JSON records can be lost after restarts, sleep, or redeploys. This deployment is suitable for a demo; persistent History requires a persistent disk on an eligible paid service or migration to a managed database.

## External services

- **Leaflet** renders and manages the interactive map.
- **OpenStreetMap** provides the map tiles and geographic data.
- **Photon** supplies place search and reverse geocoding.
- **OSRM / FOSSGIS** supplies road routes and route steps, using separate car, foot, and bike service endpoints.
- **Overpass API** supplies nearby mapped places.

The application rate-limits OSRM requests to avoid sending requests faster than one per second. Public demo endpoints may be unavailable or rate-limited; when OSRM fails, the app can return a clearly labelled campus/straight-line fallback. A fallback is not presented as real road routing.

## Submission safety

- Never upload `.env`, `.venv/`, `__pycache__/`, compiled `.pyc` files, backups, or local route-history records.
- `.env.example` contains safe defaults; `FLASK_DEBUG` defaults to `False`.
- `history_data.json` is intentionally not included in the clean package because it can contain personal route locations. It is created automatically when a route is first recorded.

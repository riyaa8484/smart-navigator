/**
 * Smart Map Navigator - Application Controller (app.js)
 * Connects real-world place search, Leaflet map interactions, OSRM routing,
 * and educational BTITC305 DSA demonstrations.
 */

import { ApiService } from './api.js';
import Header from './components/Header.js';
import Sidebar from './components/Sidebar.js';
import LeftNav from './components/LeftNav.js';
import MapView from './components/MapView.js';
import RouteDetails from './components/RouteDetails.js';
import History from './components/History.js';

import Toast from './components/Toast.js';

class App {
  constructor() {
    this.locations = [];
    this.mapView = new MapView('mapid', {
      onMapClick: (lat, lon) => this.handleMapClick(lat, lon)
    });

    this.routeDetails = new RouteDetails();

    this.history = new History({
      onSelectHistoryItem: (item) => this.handleSelectHistoryItem(item),
      onPlanRoute: () => this.switchTab('map')
    });

    this.sidebar = new Sidebar({
      onNavigate: (params) => this.handleNavigate(params),
      onAlternatives: (params) => this.handleAlternatives(params),
      onNearbyPOIs: (loc) => this.handleNearbyPOIs(loc),
      onSelectOrigin: (loc) => {
        if (loc && loc.lat && loc.lon) {
          this.mapView.setOrigin(loc.lat, loc.lon, loc.name || 'Origin');
          this.mapView.focusLocation(loc.lat, loc.lon, 14);
        }
      },
      onSelectDestination: (loc) => {
        if (loc && loc.lat && loc.lon) {
          this.mapView.setDestination(loc.lat, loc.lon, loc.name || 'Destination');
          this.mapView.focusLocation(loc.lat, loc.lon, 14);
        }
      }
    });

    // DSA Lab removed
  }

  async init() {
    // 1. Mount Header
    const header = new Header({
      onSelectLocation: (loc) => {
        this.mapView.setDestination(loc.lat, loc.lon, loc.name);
        this.sidebar.setDestination(loc);
        Toast.info(`Destination set to ${loc.name}`);
      },
      onTabChange: (tab) => this.switchTab(tab)
    });
    document.getElementById('header-mount').appendChild(header.render());

    // 2. Mount Left Navigation
    const leftNav = new LeftNav({
      onSelect: (id) => {
        // Map navigation items to the existing application actions.
        if (id === 'plan-route') {
          // Already on the planner view; no action needed.
        } else if (id === 'explore-nearby') {
          const btnNearby = document.getElementById('btn-find-nearby');
          if (btnNearby) btnNearby.click();
        } else if (id === 'history') {
          const tabHistory = document.getElementById('tab-nav-history');
          if (tabHistory) tabHistory.click();
        } else if (id === 'settings') {
          const themeBtn = document.getElementById('theme-toggle-btn');
          if (themeBtn) themeBtn.click();
        } else if (id === 'help') {
          alert('Help documentation is not available in this demo.');
        }
      }
    });
    document.getElementById('left-nav-mount').appendChild(leftNav.render());

    // 3. Mount Planner (Sidebar component) as floating planner
    const sidebarEl = this.sidebar.render();
    sidebarEl.classList.add('floating-planner');
    const mapContainer = document.querySelector('.map-container');
    if (mapContainer) { mapContainer.appendChild(sidebarEl); }

    // Mount Route Details (inside sidebar)
    const routeDetailsMount = sidebarEl.querySelector('#route-details-mount');
    this.routeDetailsContainer = routeDetailsMount;
    const routeDetailsEl = this.routeDetails.render(null);
    this.routeDetailsContainer.appendChild(routeDetailsEl);





    // Mount History into external panel (below map)
    const historyMount = document.getElementById('history-mount');
    if (historyMount) {
      historyMount.appendChild(this.history.render());
      // Ensure history is hidden by default (map view starts visible)
      historyMount.style.display = 'none';
    }


    // 4. Initialize Map
    this.mapView.init();



    // 5. Load campus sample data for DSA demonstrations (kept separate from real map markers)
    await this.loadCampusData();
  }

  async loadCampusData() {
    try {
      this.locations = await ApiService.getLocations();
      Toast.success('Map Navigator ready. Search any location or click on map.');
    } catch (err) {
      Toast.info('Map Navigator initialized.');
    }
  }

  /**
   * Handle map clicks to pick start or end locations
   */
  async handleMapClick(lat, lon) {
    Toast.info('Resolving clicked location...');
    try {
      const geo = await ApiService.reverseGeocode(lat, lon);
      const placeName = geo.name || `Point (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
      const locObj = {
        name: placeName,
        display_name: geo.formatted_address || placeName,
        lat: lat,
        lon: lon
      };

      if (!this.sidebar.selectedSource) {
        this.sidebar.setOrigin(locObj);
        Toast.success(`Set starting point: ${placeName}`);
      } else {
        this.sidebar.setDestination(locObj);
        Toast.success(`Set destination: ${placeName}`);
      }
    } catch (e) {
      const fallbackObj = {
        name: `Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`,
        lat: lat,
        lon: lon
      };
      if (!this.sidebar.selectedSource) {
        this.sidebar.setOrigin(fallbackObj);
      } else {
        this.sidebar.setDestination(fallbackObj);
      }
    }
  }

  switchTab(tab) {
    const mapViewSection = document.getElementById('map-view-container');
    const historyMount = document.getElementById('history-mount');
    if (tab === 'map') {
      if (mapViewSection) mapViewSection.style.display = 'flex';
      if (historyMount) historyMount.style.display = 'none';
      if (this.mapView.map) this.mapView.map.invalidateSize();
    } else if (tab === 'history') {
      if (mapViewSection) mapViewSection.style.display = 'none';
      if (historyMount) historyMount.style.display = 'block';
    }
  }

  async handleNavigate({ src, dst, mode, preference }) {
    Toast.info('Calculating road route...');
    // The basemap stays in cloudy-night style even when the surrounding UI is light.
    const routeColor = '#E9E3D8';

    try {
      let result;
      if (preference && preference !== 'fastest_time') {
        // Compare direct and alternative road routes using the selected priority.
        const recResult = await ApiService.getRecommendedRoute(src, dst, preference, mode);
        if (recResult.success && recResult.top_choice) {
          const top = recResult.top_choice.route_data;
          top.src_name = this.sidebar.selectedSource?.name ||
            (typeof src === 'string' ? src : 'Origin');
          top.dst_name = this.sidebar.selectedDestination?.name ||
            (typeof dst === 'string' ? dst : 'Destination');
          this.mapView.drawRoute(top.geojson, routeColor);
          this._updateRouteDetails(top, mode);
          Toast.success(`Recommended route: ${recResult.top_choice.label}`);
          await this._recordNavigationToHistory(top, mode);
        } else {
          Toast.error(recResult.error || 'No recommended route could be calculated for this mode.');
        }
      } else {
        result = await ApiService.getRoute(src, dst, mode);
        if (result.success) {
          result.src_name = this.sidebar.selectedSource?.name ||
            (typeof src === 'string' ? src : 'Origin');
          result.dst_name = this.sidebar.selectedDestination?.name ||
            (typeof dst === 'string' ? dst : 'Destination');
          this.mapView.drawRoute(result.geojson, routeColor);
          this._updateRouteDetails(result, mode);
          if (result.is_real_routing === false) {
            Toast.info(result.disclaimer || 'Showing an offline fallback route; real mode-specific road routing was unavailable.');
          } else {
            Toast.success(`Route ready: ${result.distance_km} km (${result.duration_min} min)`);
          }
          await this._recordNavigationToHistory(result, mode);
        } else {
          Toast.error(result.error || `Could not calculate a ${mode} route. Please try again.`);
        }
      }

    } catch (err) {
      Toast.error(err.message || 'Route calculation failed.');
    }
  }

  async _recordNavigationToHistory(routeData, mode) {
    const src = routeData?.src_name || 'Origin';
    const dst = routeData?.dst_name || 'Destination';

    try {
      await ApiService.addHistory(src, dst, mode || 'driving', {
        distance_km: routeData?.distance_km,
        duration_min: routeData?.duration_min
      });
      await this.history.load();
    } catch (err) {
      // A history write failure must not undo an otherwise successful route.
      console.warn('Route calculated, but history could not be updated:', err);
      Toast.warning('Route calculated, but it could not be added to History.');
    }
  }

  async handleAlternatives({ src, dst, mode }) {
    Toast.info('Finding route alternatives...');
    try {
      const res = await ApiService.getRouteAlternatives(src, dst, mode);
      if (res.success && res.alternatives) {
        this.mapView.drawAlternatives(res.alternatives);
        Toast.success(`Found ${res.alternatives.length} route options.`);
      }
    } catch (err) {
      Toast.error(err.message || 'Could not fetch route alternatives.');
    }
  }

  async handleNearbyPOIs(point) {
    const lat = point ? point.lat : (this.sidebar.selectedSource?.lat || 28.6139);
    const lon = point ? point.lon : (this.sidebar.selectedSource?.lon || 77.2090);
    const name = point?.name || 'selected location';

    Toast.info(`Searching amenities near ${name}...`);
    try {
      const pois = await ApiService.getNearby(lat, lon, 'police', 3000);
      this.mapView.setNearbyPOIs(pois);
      Toast.success(`Loaded ${pois.length} nearby places.`);
    } catch (err) {
      Toast.error('Could not fetch nearby amenities.');
    }
  }

  handleSelectHistoryItem(item) {
    this.sidebar.setValues(item.src, item.dst);
    this.handleNavigate({ src: item.src, dst: item.dst, mode: item.mode || 'driving' });
  }

  _updateRouteDetails(routeData, mode) {
    const mapContainer = document.querySelector('.map-container');

    // Remove the previous floating summary
    const oldSummary = mapContainer?.querySelector('.floating-summary');
    if (oldSummary) {
      oldSummary.remove();
    }

    // Render the updated route details inside the planner
    this.routeDetailsContainer.innerHTML = '';

    const detailsData = {
      ...routeData,
      mode: mode
    };

    const detailsElement = this.routeDetails.render(detailsData);

    this.routeDetailsContainer.appendChild(detailsElement);

    // Move the actual route summary onto the map
    const summaryCard = detailsElement.querySelector('.route-summary-card');

    if (summaryCard && mapContainer) {
      summaryCard.classList.add('floating-summary');
      mapContainer.appendChild(summaryCard);
    }
  }
}
// Bootstrap on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});

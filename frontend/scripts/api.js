/**
 * Smart Campus Map Navigator - API Service Layer (api.js)
 * Robust fetch client for connecting frontend to Flask backend APIs.
 * Supports auto-detection of host, error handling, debouncing, and loading dispatch.
 */

// Auto-detect base URL: defaults to current origin or http://localhost:5000 if opened directly via file:// or Live Server
const API_BASE = (window.location.protocol.startsWith('http')) 
  ? '' 
  : 'http://localhost:5000';

class ApiService {
  /**
   * Core request helper with status checks and JSON parsing
   */
  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! Status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error on [${config.method || 'GET'}] ${endpoint}:`, error.message);
      throw error;
    }
  }

  // --------------------------------------------------------------------------
  // 1. Real-World Place Search & Geocoding (Photon & Campus)
  // --------------------------------------------------------------------------
  static async searchPlaces(query, limit = 8, lat = null, lon = null) {
    if (!query || !query.trim()) return [];
    let url = `/api/search?q=${encodeURIComponent(query.trim())}&limit=${limit}`;
    if (lat !== null && lon !== null) {
      url += `&lat=${lat}&lon=${lon}`;
    }
    const data = await this.request(url);
    return data.results || [];
  }

  static async reverseGeocode(lat, lon) {
    return this.request(`/api/reverse-geocode?lat=${lat}&lon=${lon}`);
  }

  static async getLocations() {
    return this.request('/api/locations');
  }

  static async searchLocations(query) {
    if (!query) return this.getLocations();
    return this.request(`/api/locations/search?q=${encodeURIComponent(query)}`);
  }

  // --------------------------------------------------------------------------
  // 2. Real Routing
  // --------------------------------------------------------------------------
  static async getRoute(src, dst, mode = 'driving') {
    return this.request('/api/route', {
      method: 'POST',
      body: JSON.stringify({ src, dst, mode })
    });
  }

  static async getRouteAlternatives(src, dst, mode = 'driving') {
    return this.request('/api/route/alternatives', {
      method: 'POST',
      body: JSON.stringify({ src, dst, mode })
    });
  }

  static async getRecommendedRoute(src, dst, preference = 'fastest_time', mode = 'driving') {
    return this.request('/api/route/recommend', {
      method: 'POST',
      body: JSON.stringify({ src, dst, preference, mode })
    });
  }

  static async getNearby(lat, lon, type = 'police', radius = 2000) {
    return this.request(`/api/nearby?lat=${lat}&lon=${lon}&category=${type}&radius=${radius}`);
  }

  // --------------------------------------------------------------------------
  // 3. Navigation History (Dual Stack)
  // --------------------------------------------------------------------------
  static async getHistory(limit = 20) {
    return this.request(`/api/history?limit=${limit}`);
  }

  static async addHistory(src, dst, mode = 'driving', metrics = {}) {
    return this.request('/api/history', {
      method: 'POST',
      body: JSON.stringify({
        src,
        dst,
        mode,
        distance_km: metrics.distance_km ?? null,
        duration_min: metrics.duration_min ?? null
      })
    });
  }

  static async deleteHistory(id) {
    return this.request(`/api/history/${id}`, { method: 'DELETE' });
  }

  static async historyBack() {
    return this.request('/api/history/back', { method: 'POST' });
  }

  static async historyForward() {
    return this.request('/api/history/forward', { method: 'POST' });
  }

  static async historyUndo() {
    return this.request('/api/history/undo', { method: 'POST' });
  }

  // --------------------------------------------------------------------------
  // 4. DSA Lab Demonstrations
  // --------------------------------------------------------------------------
  static async runStack(payload) {
    return this.request('/api/dsa/stack', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runQueue(payload) {
    return this.request('/api/dsa/queue', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runCircularQueue(payload) {
    return this.request('/api/dsa/circular-queue', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runPriorityQueue(payload) {
    return this.request('/api/dsa/priority-queue', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runLinkedList(payload) {
    return this.request('/api/dsa/linked-list', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runTrees(payload) {
    return this.request('/api/dsa/trees', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runHashing(payload) {
    return this.request('/api/dsa/hashing', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runHeaps(payload) {
    return this.request('/api/dsa/heaps', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runSearch(payload) {
    return this.request('/api/dsa/search', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async runSort(payload) {
    return this.request('/api/dsa/sort', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  static async getGraphBFS(start, end) {
    return this.request('/api/graph/bfs', {
      method: 'POST',
      body: JSON.stringify({ start, end })
    });
  }

  static async getGraphMSTPrim() {
    return this.request('/api/graph/mst/prim');
  }

  static async getComplexity(algorithm) {
    const query = algorithm ? `?algorithm=${encodeURIComponent(algorithm)}` : '';
    return this.request(`/api/dsa/complexity${query}`);
  }
}

/**
 * Utility debounce function to limit API request frequency on user typing.
 */
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export { ApiService, debounce };


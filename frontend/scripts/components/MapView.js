/**
 * MapView Component (MapView.js)
 * Wraps Leaflet.js interactive OpenStreetMap rendering.
 * Supports:
 * - Dedicated Origin and Destination rounded-rectangle badge pins
 * - Real road route geometry and genuine alternative paths
 * - Map click-to-pick location callbacks
 * - Real nearby place markers
 * - No automatic clutter of arbitrary campus nodes on load
 */

class MapView {
  constructor(containerId = 'mapid', { onMapClick = null } = {}) {
    this.containerId = containerId;
    this.onMapClick = onMapClick;
    this.map = null;
    this.routeLayer = null;
    this.poiLayer = null;
    this.originMarker = null;
    this.destinationMarker = null;
    this.defaultCenter = [28.6139, 77.2090]; // Delhi NCR metropolitan area
    this.defaultZoom = 12;
  }

  init() {
    if (this.map) return;

    // Initialize Leaflet map
    this.map = L.map(this.containerId, {
      zoomControl: true,
      attributionControl: true
    }).setView(this.defaultCenter, this.defaultZoom);

    // Keep the cartographic treatment independent from the UI light/dark theme.
    // This gives the pastel interface a consistent cloudy-night navigation map.
    this.map.getContainer().classList.add('cloudy-night-map');

    // OpenStreetMap Standard Carto Tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    // Layer groups for routes and facilities
    this.routeLayer = L.layerGroup().addTo(this.map);
    this.poiLayer = L.layerGroup().addTo(this.map);

    // Listen for map clicks
    this.map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      if (this.onMapClick) {
        this.onMapClick(lat, lng);
      }
    });
  }

  /**
   * Set Origin Marker (Sleek Rounded-Rectangle Pin)
   */
  setOrigin(lat, lon, label = 'Starting Point') {
    if (!this.map) return;
    if (this.originMarker) {
      this.map.removeLayer(this.originMarker);
      this.originMarker = null;
    }

    const icon = L.divIcon({
      className: 'map-pin-origin',
      html: `
        <div style="background:#C8E8C5;color:#253329;padding:5px 10px;border-radius:8px;font-size:12px;font-weight:600;display:flex;align-items:center;gap:5px;box-shadow:0 0 0 1px rgba(147, 201, 142, 0.25);border:2px solid #93C98E;white-space:nowrap;">
          <span style="font-size:10px;">🟢</span> ${label}
        </div>
      `,
      iconSize: [120, 32],
      iconAnchor: [60, 32]
    });

    this.originMarker = L.marker([lat, lon], { icon }).addTo(this.map);
    this.originMarker.bindPopup(`<strong>Origin:</strong> ${label}<br><span style="font-size:11px;color:#64748b;">${lat.toFixed(5)}, ${lon.toFixed(5)}</span>`);
  }

  /**
   * Set Destination Marker (Sleek Rounded-Rectangle Pin)
   */
  setDestination(lat, lon, label = 'Destination') {
    if (!this.map) return;
    if (this.destinationMarker) {
      this.map.removeLayer(this.destinationMarker);
      this.destinationMarker = null;
    }

    const icon = L.divIcon({
      className: 'map-pin-destination',
      html: `
        <div style="background:#D17B70;color:#253329;padding:5px 10px;border-radius:8px;font-size:12px;font-weight:600;display:flex;align-items:center;gap:5px;box-shadow:0 0 0 1px rgba(185, 94, 86, 0.2);border:2px solid #B95E56;white-space:nowrap;">
          <span style="font-size:10px;">🔴</span> ${label}
        </div>
      `,
      iconSize: [120, 32],
      iconAnchor: [60, 32]
    });

    this.destinationMarker = L.marker([lat, lon], { icon }).addTo(this.map);
    this.destinationMarker.bindPopup(`<strong>Destination:</strong> ${label}<br><span style="font-size:11px;color:#64748b;">${lat.toFixed(5)}, ${lon.toFixed(5)}</span>`);
  }

  clearOrigin() {
    if (this.originMarker && this.map) {
      this.map.removeLayer(this.originMarker);
      this.originMarker = null;
    }
  }

  clearDestination() {
    if (this.destinationMarker && this.map) {
      this.map.removeLayer(this.destinationMarker);
      this.destinationMarker = null;
    }
  }

  /**
   * Draw primary road route from GeoJSON FeatureCollection
   */
  drawRoute(geojson, color = '#EF8D80', fitBounds = true) {
    if (!this.routeLayer) return;
    this.routeLayer.clearLayers();

    if (!geojson || !geojson.features) return;

    // Draw a soft casing first. In dark mode it becomes a muted cloudy halo;
    // in light mode it retains the warm pastel casing.
    const darkMap = this.map.getContainer().classList.contains('cloudy-night-map');
    const casingLayer = L.geoJSON(geojson, {
      style: () => ({
        color: darkMap ? '#BDB5A5' : '#F5BDA7',
        weight: darkMap ? 11 : 8,
        opacity: darkMap ? 0.38 : 0.35,
        className: 'route-cloud-halo',
        lineCap: 'round',
        lineJoin: 'round'
      }),
      filter: (feature) => feature.geometry.type === 'LineString'
    });
    this.routeLayer.addLayer(casingLayer);

    const mainLayer = L.geoJSON(geojson, {
      style: (feature) => ({
        color: color,
        weight: 4.5,
        opacity: 0.98,
        className: 'route-cloud-core',
        lineCap: 'round',
        lineJoin: 'round'
      }),
      pointToLayer: (feature, latlng) => {
        const props = feature.properties || {};
        const isPolice = (props.amenity === 'police');
        const isHospital = (props.amenity === 'hospital');
        const markerColor = isPolice ? '#B91C1C' : (isHospital ? '#0F766E' : '#475569');
        const iconChar = isPolice ? '👮' : (isHospital ? '🏥' : '📍');

        return L.marker(latlng, {
          icon: L.divIcon({
            className: 'custom-poi-marker',
            html: `<div style="background:${markerColor};color:#fff;width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 3px 6px rgba(0,0,0,0.25);font-size:14px;">${iconChar}</div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
          })
        }).bindPopup(`<strong>${props.name}</strong><br>${props.amenity || 'Waypoint'}`);
      }
    });

    this.routeLayer.addLayer(mainLayer);

    if (fitBounds && mainLayer.getBounds().isValid()) {
      this.map.fitBounds(mainLayer.getBounds(), { padding: [50, 50], maxZoom: 16 });
    }
  }

  /**
   * Draw genuine route alternatives
   */
  drawAlternatives(alternatives = []) {
    if (!this.routeLayer) return;
    this.routeLayer.clearLayers();

    const darkMap = this.map?.getContainer().classList.contains('cloudy-night-map');
    const colors = darkMap ? ['#E9E6DE', '#AEB9C8', '#C9C1B4'] : ['#EF8D80', '#A9C9E8', '#E9A1AA'];

    alternatives.forEach((alt, idx) => {
      const coords = alt.geometry; // [[lon, lat], ...]
      if (!coords || coords.length === 0) return;

      const latlngs = coords.map(c => [c[1], c[0]]);
      const isPrimary = (idx === 0);

      const polyline = L.polyline(latlngs, {
        color: colors[idx % colors.length],
        weight: isPrimary ? 6 : 4,
        opacity: isPrimary ? 0.95 : 0.65,
        dashArray: isPrimary ? null : '6, 8'
      }).bindPopup(`<strong>${alt.name}</strong><br>${alt.distance_km} km • ${alt.duration_min} min<br><span style="font-size:11px;color:#64748b;">${alt.summary || ''}</span>`);

      this.routeLayer.addLayer(polyline);
    });

    if (alternatives.length > 0) {
      const firstCoords = alternatives[0].geometry.map(c => [c[1], c[0]]);
      this.map.fitBounds(L.polyline(firstCoords).getBounds(), { padding: [50, 50] });
    }
  }

  /**
   * Render nearby mapped places / POIs
   */
  setNearbyPOIs(pois = []) {
    if (!this.poiLayer) return;
    this.poiLayer.clearLayers();

    pois.forEach(poi => {
      const coords = poi.geometry.coordinates; // [lon, lat]
      const props = poi.properties;
      const isPolice = props.amenity === 'police';
      const isHosp = props.amenity === 'hospital' || props.amenity === 'clinic';
      const isPharmacy = props.amenity === 'pharmacy';
      const isFuel = props.amenity === 'fuel';
      const isAtm = props.amenity === 'atm' || props.amenity === 'bank';

      let icon = '📍';
      let bg = '#475569';
      if (isPolice) { icon = '👮'; bg = '#B91C1C'; }
      else if (isHosp) { icon = '🏥'; bg = '#0F766E'; }
      else if (isPharmacy) { icon = '💊'; bg = '#0284C7'; }
      else if (isFuel) { icon = '⛽'; bg = '#D97706'; }
      else if (isAtm) { icon = '🏧'; bg = '#15803D'; }

      const marker = L.marker([coords[1], coords[0]], {
        icon: L.divIcon({
          className: 'poi-pin',
          html: `<div style="background:${bg};color:#fff;width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.2);font-size:13px;">${icon}</div>`,
          iconSize: [28, 28]
        })
      });

      const popupContent = document.createElement('div');
      popupContent.style.fontFamily = 'sans-serif';
      popupContent.style.padding = '4px';
      popupContent.innerHTML = `
        <strong style="color:#0f172a;font-size:13px;">${props.name}</strong>
        <div style="font-size:11px;color:#475569;margin:2px 0;">${props.amenity || 'Facility'} • ${poi.distance} km away</div>
        <div style="font-size:11px;color:#64748b;">${props.address || ''}</div>
      `;

      marker.bindPopup(popupContent);
      this.poiLayer.addLayer(marker);
    });

    if (pois.length > 0) {
      const latlngs = pois.map(p => [p.geometry.coordinates[1], p.geometry.coordinates[0]]);
      this.map.fitBounds(L.latLngBounds(latlngs), { padding: [50, 50], maxZoom: 16 });
    }
  }

  focusLocation(lat, lon, zoom = 16) {
    if (this.map) {
      this.map.flyTo([lat, lon], zoom, { duration: 1.0 });
    }
  }

  resetView() {
    if (this.map) {
      this.map.flyTo(this.defaultCenter, this.defaultZoom);
    }
  }
}

export default MapView;

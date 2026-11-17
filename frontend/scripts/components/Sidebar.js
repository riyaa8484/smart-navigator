/**
 * Sidebar Component (Sidebar.js)
 * Real-world location search-as-you-type inputs with Photon API autocomplete,
 * travel mode selection, and routing actions.
 */

import { ApiService, debounce } from '../api.js';

class Sidebar {
  constructor({
    onNavigate,
    onAlternatives,
    onNearbyPOIs,
    onSelectOrigin,
    onSelectDestination
  }) {
    this.onNavigate = onNavigate;
    this.onAlternatives = onAlternatives;
    this.onNearbyPOIs = onNearbyPOIs;
    this.onSelectOrigin = onSelectOrigin;
    this.onSelectDestination = onSelectDestination;

    this.currentMode = 'driving';
    this.selectedSource = null;       // { name, lat, lon, display_name }
    this.selectedDestination = null;  // { name, lat, lon, display_name }
    this.container = null;
  }

  render() {
    const aside = document.createElement('aside');
    aside.className = 'sidebar';
    aside.setAttribute('role', 'complementary');
    aside.setAttribute('aria-label', 'Route Selection Panel');

    aside.innerHTML = `
      <!-- Routing Panel Section -->
      <section class="sidebar-section" aria-labelledby="heading-navigate">
        <div class="sidebar-header-row">
          <h2 id="heading-navigate" class="section-heading">Plan your route</h2>
          <span class="engine-badge">OSRM • Photon</span>
        </div>

        <!-- Travel Mode Toggle (Rounded Rectangle Group) -->
        <div class="mode-toggle-group" role="radiogroup" aria-label="Travel Mode">
          <button type="button" id="mode-driving-btn" class="mode-btn active" role="radio" aria-checked="true">
            🚗 Drive
          </button>
          <button type="button" id="mode-walking-btn" class="mode-btn" role="radio" aria-checked="false">
            🚶 Walk
          </button>
          <button type="button" id="mode-cycling-btn" class="mode-btn" role="radio" aria-checked="false">
            🚲 Bike
          </button>
        </div>

        <!-- Location Inputs Container -->
        <div class="location-inputs-box">
          <!-- Origin Location Search -->
          <div class="location-field-wrapper">
            <label for="source-search-input">
              <span class="pin-indicator pin-start">🟢</span> From (Origin)
            </label>
            <div class="search-box-row">
              <input
                type="text"
                id="source-search-input"
                class="location-input"
                placeholder="Search place, address, or click map..."
                autocomplete="off"
                aria-label="Origin place search"
              />
              <button type="button" id="btn-clear-source" class="input-clear-btn" title="Clear origin" aria-label="Clear origin">✕</button>
            </div>
            <ul id="source-autocomplete-dropdown" class="location-dropdown" style="display:none;" role="listbox"></ul>
          </div>

          <!-- Swap Button -->
          <div class="swap-row">
            <button type="button" id="btn-swap-locations" class="btn-swap" title="Swap Origin and Destination" aria-label="Swap Origin and Destination">
              ⇅
            </button>
          </div>

          <!-- Destination Location Search -->
          <div class="location-field-wrapper">
            <label for="destination-search-input">
              <span class="pin-indicator pin-end">🔴</span> To (Destination)
            </label>
            <div class="search-box-row">
              <input
                type="text"
                id="destination-search-input"
                class="location-input"
                placeholder="Search place, address, or click map..."
                autocomplete="off"
                aria-label="Destination place search"
              />
              <button type="button" id="btn-clear-dest" class="input-clear-btn" title="Clear destination" aria-label="Clear destination">✕</button>
            </div>
            <ul id="dest-autocomplete-dropdown" class="location-dropdown" style="display:none;" role="listbox"></ul>
          </div>
        </div>

        <!-- Priority Preference Selection -->
        <div class="field-group">
          <label for="preference-select">Routing Priority</label>
          <select id="preference-select" class="input-select" aria-label="Route scoring preference">
            <option value="fastest_time">Fastest Time (Recommended)</option>
            <option value="shortest_distance">Shortest Distance</option>
            <option value="minimal_detour">Minimal Detour Deviation</option>
          </select>
        </div>

        <!-- Action Buttons (Rounded Rectangles) -->
        <button type="button" id="btn-calculate-route" class="btn-primary" aria-label="Calculate road route">
          <span>Get Directions</span> ➔
        </button>

        <div class="btn-group-row">
          <button type="button" id="btn-show-alternatives" class="btn-secondary" title="View multiple route alternatives">
            Alternative Routes
          </button>
          <button type="button" id="btn-find-nearby" class="btn-secondary" title="Search amenities near selected location">
            Explore Nearby
          </button>
        </div>
      </section>

      <!-- Mount point for Route Details & Turn-by-Turn Directions -->
      <div id="route-details-mount"></div>


    `;

    this._bindEvents(aside);
    this.container = aside;
    return aside;
  }

  _bindEvents(container) {
    const srcInput = container.querySelector('#source-search-input');
    const dstInput = container.querySelector('#destination-search-input');
    const srcDropdown = container.querySelector('#source-autocomplete-dropdown');
    const dstDropdown = container.querySelector('#dest-autocomplete-dropdown');
    const btnClearSrc = container.querySelector('#btn-clear-source');
    const btnClearDst = container.querySelector('#btn-clear-dest');
    const btnSwap = container.querySelector('#btn-swap-locations');

    const modeDrivingBtn = container.querySelector('#mode-driving-btn');
    const modeWalkingBtn = container.querySelector('#mode-walking-btn');
    const modeCyclingBtn = container.querySelector('#mode-cycling-btn');

    const btnGo = container.querySelector('#btn-calculate-route');
    const btnAlt = container.querySelector('#btn-show-alternatives');
    const btnNearby = container.querySelector('#btn-find-nearby');


    // 1. Search-as-you-type Autocomplete for Origin
    const debouncedSearchSrc = debounce(async (q) => {
      if (!q || q.length < 2) {
        srcDropdown.style.display = 'none';
        return;
      }
      try {
        const results = await ApiService.searchPlaces(q, 6);
        this._renderDropdown(srcDropdown, results, (item) => {
          this.setOrigin({
            name: item.name,
            lat: item.lat,
            lon: item.lon,
            display_name: item.display_name
          });
          srcDropdown.style.display = 'none';
        });
      } catch (e) {
        srcDropdown.style.display = 'none';
      }
    }, 280);

    srcInput.addEventListener('input', (e) => debouncedSearchSrc(e.target.value));

    // 2. Search-as-you-type Autocomplete for Destination
    const debouncedSearchDst = debounce(async (q) => {
      if (!q || q.length < 2) {
        dstDropdown.style.display = 'none';
        return;
      }
      try {
        const results = await ApiService.searchPlaces(q, 6);
        this._renderDropdown(dstDropdown, results, (item) => {
          this.setDestination({
            name: item.name,
            lat: item.lat,
            lon: item.lon,
            display_name: item.display_name
          });
          dstDropdown.style.display = 'none';
        });
      } catch (e) {
        dstDropdown.style.display = 'none';
      }
    }, 280);

    dstInput.addEventListener('input', (e) => debouncedSearchDst(e.target.value));

    // Close dropdowns on click outside
    document.addEventListener('click', (e) => {
      if (!container.contains(e.target)) {
        srcDropdown.style.display = 'none';
        dstDropdown.style.display = 'none';
      }
    });

    // Clear buttons
    btnClearSrc.addEventListener('click', () => {
      srcInput.value = '';
      this.selectedSource = null;
      srcDropdown.style.display = 'none';
    });

    btnClearDst.addEventListener('click', () => {
      dstInput.value = '';
      this.selectedDestination = null;
      dstDropdown.style.display = 'none';
    });

    // Swap Origin and Destination
    btnSwap.addEventListener('click', () => {
      const tempLoc = this.selectedSource;
      const tempVal = srcInput.value;

      this.selectedSource = this.selectedDestination;
      srcInput.value = dstInput.value;

      this.selectedDestination = tempLoc;
      dstInput.value = tempVal;

      if (this.selectedSource && this.onSelectOrigin) {
        this.onSelectOrigin(this.selectedSource);
      }
      if (this.selectedDestination && this.onSelectDestination) {
        this.onSelectDestination(this.selectedDestination);
      }
    });

    // Travel Mode Toggle
    const setMode = (mode, activeBtn) => {
      this.currentMode = mode;
      [modeDrivingBtn, modeWalkingBtn, modeCyclingBtn].forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-checked', 'false');
      });
      activeBtn.classList.add('active');
      activeBtn.setAttribute('aria-checked', 'true');
    };

    modeDrivingBtn.addEventListener('click', () => setMode('driving', modeDrivingBtn));
    modeWalkingBtn.addEventListener('click', () => setMode('walking', modeWalkingBtn));
    modeCyclingBtn.addEventListener('click', () => setMode('cycling', modeCyclingBtn));

    // Calculate Route
    btnGo.addEventListener('click', () => {
      const src = this.selectedSource ? [this.selectedSource.lat, this.selectedSource.lon] : srcInput.value.trim();
      const dst = this.selectedDestination ? [this.selectedDestination.lat, this.selectedDestination.lon] : dstInput.value.trim();
      const preference = container.querySelector('#preference-select').value;

      if (!src || !dst) {
        alert('Please specify both an Origin and a Destination.');
        return;
      }

      if (this.onNavigate) {
        this.onNavigate({
          src,
          dst,
          mode: this.currentMode,
          preference
        });
      }
    });

    // Alternative Routes
    btnAlt.addEventListener('click', () => {
      const src = this.selectedSource ? [this.selectedSource.lat, this.selectedSource.lon] : srcInput.value.trim();
      const dst = this.selectedDestination ? [this.selectedDestination.lat, this.selectedDestination.lon] : dstInput.value.trim();

      if (!src || !dst) {
        alert('Please specify both an Origin and a Destination to compare alternatives.');
        return;
      }

      if (this.onAlternatives) {
        this.onAlternatives({ src, dst, mode: this.currentMode });
      }
    });

    // Nearby POIs
    btnNearby.addEventListener('click', () => {
      const point = this.selectedSource || this.selectedDestination;
      if (this.onNearbyPOIs) {
        this.onNearbyPOIs(point);
      }
    });
  }

  _renderDropdown(dropdownEl, items, onSelect) {
    dropdownEl.innerHTML = '';
    if (!items || items.length === 0) {
      dropdownEl.innerHTML = '<li class="dropdown-item-empty">No matching places found</li>';
      dropdownEl.style.display = 'block';
      return;
    }

    items.forEach(item => {
      const li = document.createElement('li');
      li.className = 'dropdown-item';
      li.setAttribute('role', 'option');

      const catBadge = item.category ? `<span class="category-pill">${item.category.replace(/_/g, ' ')}</span>` : '';
      const addressText = item.display_name || `${item.lat.toFixed(4)}, ${item.lon.toFixed(4)}`;

      li.innerHTML = `
        <div class="dropdown-item-title">
          <span>${item.name}</span>
          ${catBadge}
        </div>
        <div class="dropdown-item-address">${addressText}</div>
      `;

      li.addEventListener('click', (e) => {
        e.stopPropagation();
        onSelect(item);
      });

      dropdownEl.appendChild(li);
    });

    dropdownEl.style.display = 'block';
  }

  setOrigin(loc) {
    this.selectedSource = loc;
    if (this.container) {
      const inp = this.container.querySelector('#source-search-input');
      if (inp) inp.value = loc.name || loc.display_name;
    }
    if (this.onSelectOrigin) {
      this.onSelectOrigin(loc);
    }
  }

  setDestination(loc) {
    this.selectedDestination = loc;
    if (this.container) {
      const inp = this.container.querySelector('#destination-search-input');
      if (inp) inp.value = loc.name || loc.display_name;
    }
    if (this.onSelectDestination) {
      this.onSelectDestination(loc);
    }
  }

  setValues(src, dst) {
    if (!this.container) return;
    if (src) {
      const inp = this.container.querySelector('#source-search-input');
      if (inp) inp.value = typeof src === 'string' ? src : `${src[0].toFixed(4)}, ${src[1].toFixed(4)}`;
      this.selectedSource = typeof src === 'string' ? { name: src } : { name: 'Origin', lat: src[0], lon: src[1] };
    }
    if (dst) {
      const inp = this.container.querySelector('#destination-search-input');
      if (inp) inp.value = typeof dst === 'string' ? dst : `${dst[0].toFixed(4)}, ${dst[1].toFixed(4)}`;
      this.selectedDestination = typeof dst === 'string' ? { name: dst } : { name: 'Destination', lat: dst[0], lon: dst[1] };
    }
  }
}

export default Sidebar;

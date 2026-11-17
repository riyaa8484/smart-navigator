/**
 * Header Component (Header.js)
 * Global navigation, instant building search, theme toggler, and tab switching.
 */

import { ApiService, debounce } from '../api.js';

class Header {
  constructor({ onSelectLocation, onTabChange }) {
    this.onSelectLocation = onSelectLocation;
    this.onTabChange = onTabChange;
    this.currentTheme = localStorage.getItem('app-theme') || 'dark';
    this.currentPalette = localStorage.getItem('app-palette') || 'theme-a';
  }

  render() {
    const header = document.createElement('header');
    header.className = 'app-header';
    header.setAttribute('role', 'banner');

    header.innerHTML = `


      <!-- Quick Building Search -->
      <div class="header-search">
        <div class="search-input-wrapper">
          <span class="search-icon" aria-hidden="true">🔍</span>
          <input 
            type="search" 
            id="global-search-input" 
            class="search-input" 
            placeholder="Search any place or address (e.g. India Gate, NSUT)..." 
            aria-label="Search places and addresses"
            autocomplete="off"
          />
        </div>
        <ul id="search-autocomplete-list" class="autocomplete-dropdown" style="display:none;" role="listbox"></ul>
      </div>

      <!-- Controls & Tabs -->
      <div class="header-controls">
        <!-- View Navigation Tabs -->
        <nav class="nav-tabs" role="tablist" aria-label="Main Navigation">
          <button id="tab-nav-map" class="tab-btn active" role="tab" aria-selected="true">Map View</button>
          <button id="tab-nav-history" class="tab-btn" role="tab" aria-selected="false">History</button>
        </nav>

        <!-- Color Palette Dropdown -->
        <select id="palette-selector" class="icon-btn" style="width:auto;padding:4px 8px;font-size:0.75rem;" aria-label="Select Color Theme">
          <option value="theme-a">Charcoal Rose</option>
          <option value="theme-b">Navy</option>
          <option value="theme-c">Purple</option>
        </select>

        <!-- Dark/Light Mode Button -->
        <button id="theme-toggle-btn" class="icon-btn" aria-label="Toggle Dark Mode" title="Toggle Dark/Light Mode">
          <span id="theme-icon">🌙</span>
        </button>
      </div>
    `;

    this._bindEvents(header);
    this._applyTheme();
    return header;
  }

  _bindEvents(container) {
    const searchInput = container.querySelector('#global-search-input');
    const autoList = container.querySelector('#search-autocomplete-list');
    const themeBtn = container.querySelector('#theme-toggle-btn');
    const paletteSelect = container.querySelector('#palette-selector');
    const tabMap = container.querySelector('#tab-nav-map');
    const tabHistory = container.querySelector('#tab-nav-history'); // new History tab
    const tabDsa = container.querySelector('#tab-nav-dsa'); // may be null after DSA removal

    paletteSelect.value = this.currentPalette;

    // Tab switcher for Map view (always present)
    tabMap.addEventListener('click', () => {
      tabMap.classList.add('active');
      tabMap.setAttribute('aria-selected', 'true');
      if (tabDsa) {
        tabDsa.classList.remove('active');
        tabDsa.setAttribute('aria-selected', 'false');
      }
      if (tabHistory) {
        tabHistory.classList.remove('active');
        tabHistory.setAttribute('aria-selected', 'false');
      }
      if (this.onTabChange) this.onTabChange('map');
    });

    // Tab switcher for History view (new)
    if (tabHistory) {
      tabHistory.addEventListener('click', () => {
        tabHistory.classList.add('active');
        tabHistory.setAttribute('aria-selected', 'true');
        tabMap.classList.remove('active');
        tabMap.setAttribute('aria-selected', 'false');
        if (tabDsa) {
          tabDsa.classList.remove('active');
          tabDsa.setAttribute('aria-selected', 'false');
        }
        if (this.onTabChange) this.onTabChange('history');
      });
    }

    // Optional DSA tab handling (only if element exists)
    if (tabDsa) {
      tabDsa.addEventListener('click', () => {
        tabDsa.classList.add('active');
        tabDsa.setAttribute('aria-selected', 'true');
        tabMap.classList.remove('active');
        tabMap.setAttribute('aria-selected', 'false');
        if (this.onTabChange) this.onTabChange('dsa');
      });
    }

    // Theme Toggle
    themeBtn.addEventListener('click', () => {
      this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
      localStorage.setItem('app-theme', this.currentTheme);
      this._applyTheme();
    });

    // Palette Selector
    paletteSelect.addEventListener('change', (e) => {
      this.currentPalette = e.target.value;
      localStorage.setItem('app-palette', this.currentPalette);
      this._applyTheme();
    });

    // Debounced Search Input (280ms)
    const handleSearch = debounce(async (query) => {
      if (!query || query.trim().length === 0) {
        autoList.style.display = 'none';
        return;
      }
      try {
        const results = await ApiService.searchPlaces(query.trim(), 6);
        if (results && results.length > 0) {
          autoList.innerHTML = results.map((loc, idx) => `
            <li class="autocomplete-item" role="option" data-idx="${idx}">
              <div>
                <strong>${loc.name}</strong>
                <div style="font-size:0.75rem;color:var(--color-text-muted);">${loc.display_name || ''}</div>
              </div>
              <span style="font-size:0.75rem;color:var(--color-primary);">📍</span>
            </li>
          `).join('');
          autoList.style.display = 'block';

          // Attach click listeners to suggestions
          autoList.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => {
              const idx = parseInt(item.getAttribute('data-idx'), 10);
              const found = results[idx];
              searchInput.value = found.name;
              autoList.style.display = 'none';
              if (this.onSelectLocation) this.onSelectLocation(found);
            });
          });
        } else {
          autoList.innerHTML = `<li class="autocomplete-item" style="color:var(--color-text-muted);">No matching places found</li>`;
          autoList.style.display = 'block';
        }
      } catch (err) {
        autoList.style.display = 'none';
      }
    }, 280);

    searchInput.addEventListener('input', (e) => handleSearch(e.target.value));

    // Close autocomplete on click outside
    document.addEventListener('click', (e) => {
      if (!container.querySelector('.header-search').contains(e.target)) {
        autoList.style.display = 'none';
      }
    });
  }

  _applyTheme() {
    const root = document.documentElement;
    root.setAttribute('data-theme', this.currentTheme);
    root.setAttribute('data-palette', this.currentPalette);

    const icon = document.querySelector('#theme-icon');
    if (icon) {
      icon.textContent = this.currentTheme === 'dark' ? '☀️' : '🌙';
    }
  }
}

export default Header;


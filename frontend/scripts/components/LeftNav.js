/**
 * Left Navigation Component (LeftNav.js)
 * Provides a vertical navigation sidebar with icons and labels.
 * Items: Plan Route, Explore Nearby, History, Settings, and Help.
 * The active item is highlighted in the current theme.
 */

class LeftNav {
  constructor({ onSelect }) {
    this.onSelect = onSelect; // callback receives item id
    this.activeId = 'plan-route';
  }

  render() {
    const nav = document.createElement('nav');
    nav.className = 'left-nav';
    nav.setAttribute('aria-label', 'Primary navigation');
    nav.innerHTML = `
      <div class="nav-brand">
        <div class="brand-logo" aria-hidden="true">🗺️</div>
        <div class="brand-title">Smart Navigator</div>
      </div>
      <ul class="nav-list top-group">
        <li class="nav-item" data-id="plan-route"><span class="nav-icon">🗺️</span><span class="nav-label">Plan Route</span></li>
        <li class="nav-item" data-id="explore-nearby"><span class="nav-icon">📍</span><span class="nav-label">Explore Nearby</span></li>
        <li class="nav-item" data-id="history"><span class="nav-icon">🕑</span><span class="nav-label">History</span></li>
      </ul>
      <ul class="nav-list bottom-group">
        <li class="nav-item" data-id="settings"><span class="nav-icon">⚙️</span><span class="nav-label">Settings</span></li>
        <li class="nav-item" data-id="help"><span class="nav-icon">❓</span><span class="nav-label">Help</span></li>
      </ul>
    `;
    // Bind click events
    nav.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = item.getAttribute('data-id');
        this._setActive(id);
        if (this.onSelect) this.onSelect(id);
      });
    });
    // Set initial active state
    this._setActive(this.activeId);
    return nav;
  }

  _setActive(id) {
    const nav = document.querySelector('.left-nav');
    if (!nav) return;
    nav.querySelectorAll('.nav-item').forEach(item => {
      const itemId = item.getAttribute('data-id');
      if (itemId === id) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
    this.activeId = id;
  }
}

export default LeftNav;


/**
 * History Component (History.js)
 * Displays JSON-backed route records with stack-based Back, Forward, and Undo controls.
 */

import { ApiService } from '../api.js';
import Toast from './Toast.js';

class History {
  constructor({ onSelectHistoryItem, onPlanRoute, onStateChange }) {
    this.onSelectHistoryItem = onSelectHistoryItem;
    this.onPlanRoute = onPlanRoute;
    this.onStateChange = onStateChange;
    this.historyItems = [];
  }

  async load() {
    try {
      this.historyItems = await ApiService.getHistory(15);
      this._renderList();
    } catch (e) {
      console.warn('Could not load history:', e);
    }
  }

  render() {
    const section = document.createElement('section');
    /* keep legacy class for compatibility and add page‑specific class */
    section.className = 'sidebar-section history-page';
    section.setAttribute('aria-labelledby', 'heading-history');

    section.innerHTML = `
      <!-- Header -->
      <div class="history-header">
        <h2 id="heading-history" class="section-heading">Your Journeys</h2>
        <p class="history-subtitle">Completed routes are recorded here automatically. Select any route to navigate again.</p>
      </div>

      <!-- Navigation controls (Back / Forward / Undo) -->
      <div class="history-controls" role="group" aria-label="History navigation controls">
        <button id="btn-hist-back" class="btn-secondary" title="Pop Back Stack">⬅ Back</button>
        <button id="btn-hist-forward" class="btn-secondary" title="Pop Forward Stack">Forward ➔</button>
        <button id="btn-hist-undo" class="btn-secondary" title="Undo Last Operation">↺ Undo</button>
      </div>

      <!-- List of route entries -->
      <ul id="history-items-container" class="history-list" role="list">
        <li class="history-empty-state">
          <div class="history-empty-icon" aria-hidden="true">🧭</div>
          <strong>No journeys yet</strong>
          <p>Your completed Drive, Walk and Bike routes will appear here automatically.</p>
          <button type="button" id="btn-history-plan" class="history-plan-button">Plan a route →</button>
        </li>
      </ul>
    `;

    this._bindEvents(section);
    this.container = section;
    this.load();
    return section;
  }

  _bindEvents(container) {
    const backBtn = container.querySelector('#btn-hist-back');
    const fwdBtn = container.querySelector('#btn-hist-forward');
    const undoBtn = container.querySelector('#btn-hist-undo');

    backBtn.addEventListener('click', async () => {
      try {
        const res = await ApiService.historyBack();
        if (res.success && res.current) {
          Toast.info(`Navigated Back to: ${res.current.dst}`);
          if (this.onSelectHistoryItem) this.onSelectHistoryItem(res.current);
        } else {
          Toast.warning('No previous locations in Back Stack.');
        }
      } catch (err) {
        Toast.error(err.message);
      }
    });

    fwdBtn.addEventListener('click', async () => {
      try {
        const res = await ApiService.historyForward();
        if (res.success && res.current) {
          Toast.info(`Navigated Forward to: ${res.current.dst}`);
          if (this.onSelectHistoryItem) this.onSelectHistoryItem(res.current);
        } else {
          Toast.warning('Forward Stack is currently empty.');
        }
      } catch (err) {
        Toast.error(err.message);
      }
    });

    const planBtn = container.querySelector('#btn-history-plan');
    if (planBtn) {
      planBtn.addEventListener('click', () => {
        if (this.onPlanRoute) this.onPlanRoute();
      });
    }

    undoBtn.addEventListener('click', async () => {
      try {
        const res = await ApiService.historyUndo();
        if (res.success) {
          Toast.success('Action undone successfully.');
          await this.load();
        } else {
          Toast.warning(res.message || 'Nothing to undo.');
        }
      } catch (err) {
        Toast.error(err.message);
      }
    });
  }

  _renderList() {
    if (!this.container) return;
    const list = this.container.querySelector('#history-items-container');
    if (!list) return;

    if (!this.historyItems || this.historyItems.length === 0) {
      list.innerHTML = `
        <li class="history-empty-state">
          <div class="history-empty-icon" aria-hidden="true">🧭</div>
          <strong>No journeys yet</strong>
          <p>Your completed Drive, Walk and Bike routes will appear here automatically.</p>
          <button type="button" id="btn-history-plan" class="history-plan-button">Plan a route →</button>
        </li>`;
      const planBtn = list.querySelector('#btn-history-plan');
      if (planBtn) planBtn.addEventListener('click', () => {
        if (this.onPlanRoute) this.onPlanRoute();
      });
      return;
    }

    list.innerHTML = this.historyItems.map(item => `
      <li class="history-item card" data-id="${item.id}" role="listitem">
        <div class="card-content">
          <div class="card-origin-destination">
            <span class="origin">${item.src}</span>
            <span class="arrow">➔</span>
            <span class="destination">${item.dst}</span>
          </div>
          <div class="card-meta">
            <span class="mode">${({driving:'Drive',walking:'Walk',cycling:'Bike'}[item.mode] || item.mode || 'Route')}</span>
            ${item.distance_km ? `<span class="distance">${item.distance_km} km</span>` : ''}
            ${item.duration_min ? `<span class="duration">${item.duration_min} min</span>` : ''}
            <span class="time">${new Date(item.time).toLocaleString([], {dateStyle:'short', timeStyle:'short'})}</span>
          </div>
        </div>
        <button class="delete-history-btn icon-btn" title="Delete" aria-label="Delete history entry">&times;</button>
      </li>
    `).join('');

    // Attach click handlers
    list.querySelectorAll('.history-item').forEach(li => {
      li.addEventListener('click', (e) => {
        if (e.target.closest('.delete-history-btn')) return;
        const id = parseInt(li.getAttribute('data-id'), 10);
        const selected = this.historyItems.find(h => h.id === id);
        if (selected && this.onSelectHistoryItem) {
          this.onSelectHistoryItem(selected);
        }
      });
    });

    list.querySelectorAll('.delete-history-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = parseInt(btn.closest('.history-item').getAttribute('data-id'), 10);
        try {
          await ApiService.deleteHistory(id);
          Toast.info('History entry removed.');
          await this.load();
        } catch (err) {
          Toast.error(err.message);
        }
      });
    });
  }
}

export default History;


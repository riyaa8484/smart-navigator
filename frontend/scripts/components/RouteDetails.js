/**
 * RouteDetails Component (RouteDetails.js)
 * Displays route summaries, turn-by-turn navigation cards, and history actions.
 */

class RouteDetails {
  render(routeData) {
    const section = document.createElement('section');
    section.className = 'sidebar-section';
    section.setAttribute('aria-labelledby', 'heading-route-details');

    if (!routeData) {
      section.innerHTML = `
        <h2 id="heading-route-details" class="section-heading">Directions & Summary</h2>
        <p style="font-size:0.8rem;color:var(--color-text-muted);">Select origin and destination above, then click Get Directions to view turn-by-turn instructions.</p>
      `;
      return section;
    }

    const dist = routeData.distance_km || 0;
    const dur = routeData.duration_min || 0;
    const srcName = routeData.src_name || 'Origin';
    const dstName = routeData.dst_name || 'Destination';
    const instructions = routeData.instructions || [];
    const modeLabels = {
      driving: '🚗 Drive',
      walking: '🚶 Walk',
      cycling: '🚲 Bike'
    };

    const modeLabel = modeLabels[routeData.mode] || '🧭 Route';

    section.innerHTML = `
      <h2 id="heading-route-details" class="section-heading">Route Details</h2>

      
<!-- Floating Route Summary Card -->
<div class="route-summary-card">

    <div class="route-summary-heading">
        <strong>${modeLabel}</strong>
        <span class="summary-step-count">
            ${instructions.length} steps
        </span>
    </div>

    <div class="route-metrics">
        <div class="summary-metric">
            <strong>${dist}</strong>
            <span>Distance · km</span>
        </div>

        <div class="summary-metric">
            <strong>${dur}</strong>
            <span>Est. time · min</span>
        </div>

        <div class="summary-metric">
            <strong>${instructions.length}</strong>
            <span>Steps</span>
        </div>
    </div>

    <div class="route-summary-destination">
        From <strong>${srcName}</strong>
        → To <strong>${dstName}</strong>
    </div>

    <button type="button" id="btn-view-steps"
            class="summary-view-steps">
        View steps →
    </button>

</div>


      <!-- Turn-by-Turn Instruction Steps -->
      <div class="section-heading">Step-by-step navigation (${instructions.length} steps)</div>
      <ul class="directions-list" role="list">
        ${instructions.length > 0 ? instructions.map((step, idx) => `
          <li class="direction-item" role="listitem">
            <div class="direction-icon" aria-hidden="true">${idx + 1}</div>
            <div>
              <div style="font-weight:500;color:var(--color-text-main);">${step.instruction}</div>
              ${step.distance_m ? `<div style="font-size:0.7rem;color:var(--color-text-muted);">${Math.round(step.distance_m)} meters (${Math.round(step.duration_s || 0)}s)</div>` : ''}
            </div>
          </li>
        `).join('') : `
          <li class="direction-item">Follow campus roadway directly to destination.</li>
        `}
      </ul>
    `;

    const viewStepsBtn = section.querySelector('#btn-view-steps');

    if (viewStepsBtn) {
      viewStepsBtn.addEventListener('click', () => {
        const directionsList = section.querySelector('.directions-list');

        if (directionsList) {
          directionsList.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    }

    return section;
  }
}

export default RouteDetails;


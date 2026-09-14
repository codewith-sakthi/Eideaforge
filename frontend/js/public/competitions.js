/**
 * competitions.js – Public competitions directory with status filters
 */

document.addEventListener('DOMContentLoaded', async () => {
  let currentFilter = 'all';

  async function loadCompetitions(status = null) {
    const listEl = document.getElementById('competitions-list');
    listEl.innerHTML = '<p style="color:var(--text-muted);text-align:center;grid-column:1/-1;">Loading challenges...</p>';

    try {
      const endpoint = status && status !== 'all' ? `/public/competitions?status=${status}` : '/public/competitions';
      const res = await api.get(endpoint);
      
      let comps = [];
      if (res.success && res.data) {
        if (Array.isArray(res.data)) {
          comps = res.data;
        } else {
          // grouped dictionary
          comps = [...(res.data.ongoing || []), ...(res.data.upcoming || []), ...(res.data.completed || [])];
        }
      }

      if (comps.length === 0) {
        listEl.innerHTML = '<p style="color:var(--text-muted);text-align:center;grid-column:1/-1;">No competitions found matching this filter.</p>';
        return;
      }

      listEl.innerHTML = comps.map(c => `
        <div class="glass-card competition-card">
          <div class="competition-card-header">
            <h3 class="competition-card-title">${utils.escapeHTML(c.title)}</h3>
            ${utils.getBadgeHTML(c.status)}
          </div>
          <p class="competition-card-desc">${utils.escapeHTML(c.description || 'No description provided.')}</p>
          <div class="competition-card-meta">
            <span>📅 ${utils.formatDate(c.start_date)} - ${utils.formatDate(c.end_date)}</span>
            <a href="/competition-details.html?id=${c.id}" class="btn btn-primary btn-sm">Details & Register</a>
          </div>
        </div>
      `).join('');
    } catch (err) {
      listEl.innerHTML = '<p style="color:var(--danger);text-align:center;grid-column:1/-1;">Failed to load competitions.</p>';
    }
  }

  // Filter tab buttons
  document.querySelectorAll('.filter-tab').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadCompetitions(btn.dataset.filter);
    });
  });

  loadCompetitions('all');
});

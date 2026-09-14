/**
 * home.js – Public landing page dynamic logic
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Load platform statistics
  try {
    const statsRes = await api.get('/public/stats');
    if (statsRes.success && statsRes.data) {
      document.getElementById('stat-ideas').textContent = statsRes.data.ideas_count || 0;
      document.getElementById('stat-teams').textContent = statsRes.data.teams_count || 0;
      document.getElementById('stat-competitions').textContent = statsRes.data.competitions_count || 0;
      document.getElementById('stat-students').textContent = statsRes.data.students_count || 0;
    }
  } catch (e) {
    console.warn('Could not load stats', e);
  }

  // Load featured/ongoing competitions
  try {
    const compRes = await api.get('/public/competitions?status=ongoing');
    const container = document.getElementById('featured-competitions');
    if (compRes.success && compRes.data && compRes.data.length > 0) {
      container.innerHTML = compRes.data.slice(0, 3).map(comp => `
        <div class="glass-card competition-card">
          <div class="competition-card-header">
            <h3 class="competition-card-title">${utils.escapeHTML(comp.title)}</h3>
            ${utils.getBadgeHTML(comp.status)}
          </div>
          <p class="competition-card-desc">${utils.escapeHTML(comp.description)}</p>
          <div class="competition-card-meta">
            <span>📅 Ends: ${utils.formatDate(comp.end_date)}</span>
            <a href="/competition-details.html?id=${comp.id}" class="btn btn-primary btn-sm">View Challenge →</a>
          </div>
        </div>
      `).join('');
    } else {
      container.innerHTML = '<p style="color:var(--text-muted);grid-column: 1/-1;text-align:center;">No active competitions right now. Check back soon!</p>';
    }
  } catch (e) {
    console.warn('Could not load competitions', e);
  }
});

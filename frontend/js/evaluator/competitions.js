/**
 * evaluator/competitions.js – Assigned competitions for evaluator
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('evaluator')) return;

  const container = document.getElementById('eval-competitions-grid');

  try {
    const res = await api.get('/evaluator/competitions');
    if (res.success && res.data) {
      if (res.data.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted); grid-column:1/-1;">You have not been assigned to any competitions yet.</p>';
        return;
      }

      container.innerHTML = res.data.map(c => `
        <div class="glass-card" style="display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.75rem;">
              <h3 style="font-size:1.25rem;">${utils.escapeHTML(c.title)}</h3>
              ${utils.getBadgeHTML(c.status)}
            </div>
            <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem;">${utils.escapeHTML(c.description || '')}</p>
            <p style="font-size:0.85rem; color:var(--text-dim); margin-bottom:1rem;">📅 Ends: ${utils.formatDate(c.end_date)}</p>
          </div>
          <a href="/evaluator/submissions.html?comp_id=${c.id}" class="btn btn-primary btn-sm">View Submissions to Score →</a>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error(err);
  }
});

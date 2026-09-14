/**
 * admin/competitions.js – Admin competition list & operations
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const tbody = document.getElementById('admin-competitions-tbody');

  async function loadCompetitions() {
    try {
      const res = await api.get('/competitions');
      if (res.success && res.data) {
        if (res.data.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No competitions created yet.</td></tr>';
          return;
        }

        tbody.innerHTML = res.data.map(c => `
          <tr>
            <td><strong>${utils.escapeHTML(c.title)}</strong></td>
            <td>${utils.getBadgeHTML(c.status)}</td>
            <td>${utils.formatDate(c.start_date)} – ${utils.formatDate(c.end_date)}</td>
            <td>
              <a href="/admin/competition-details.html?id=${c.id}" class="btn btn-secondary btn-sm">Overview</a>
              <a href="/admin/edit-competition.html?id=${c.id}" class="btn btn-primary btn-sm">Edit</a>
              <a href="/admin/evaluation-criteria.html?comp_id=${c.id}" class="btn btn-secondary btn-sm">Rubric</a>
              <a href="/admin/assign-evaluators.html?comp_id=${c.id}" class="btn btn-secondary btn-sm">Judges</a>
            </td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.error(err);
    }
  }

  loadCompetitions();
});

/**
 * admin/dashboard.js – Admin command center dashboard
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const user = auth.getUser();
  document.getElementById('user-email-display').textContent = user.email;

  try {
    const res = await api.get('/admin/dashboard');
    if (res.success && res.data) {
      const d = res.data;
      document.getElementById('count-students').textContent = d.students_count || 0;
      document.getElementById('count-ideas').textContent = d.ideas_count || 0;
      document.getElementById('count-competitions').textContent = d.competitions_count || 0;
      document.getElementById('count-evaluators').textContent = d.evaluators_count || 0;

      // Pending ideas
      const ideasBody = document.getElementById('recent-ideas-tbody');
      if (d.recent_ideas && d.recent_ideas.length > 0) {
        ideasBody.innerHTML = d.recent_ideas.map(i => `
          <tr>
            <td><strong>${utils.escapeHTML(i.title)}</strong></td>
            <td>${utils.escapeHTML(i.category || 'General')}</td>
            <td>${utils.getBadgeHTML(i.status)}</td>
            <td><a href="/admin/idea-details.html?id=${i.id}" class="btn btn-secondary btn-sm">Review</a></td>
          </tr>
        `).join('');
      } else {
        ideasBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No ideas to display.</td></tr>';
      }

      // Recent competitions
      const compsBody = document.getElementById('recent-comps-tbody');
      if (d.recent_competitions && d.recent_competitions.length > 0) {
        compsBody.innerHTML = d.recent_competitions.map(c => `
          <tr>
            <td><strong>${utils.escapeHTML(c.title)}</strong></td>
            <td>${utils.getBadgeHTML(c.status)}</td>
            <td>${utils.formatDate(c.end_date)}</td>
            <td><a href="/admin/competition-details.html?id=${c.id}" class="btn btn-secondary btn-sm">Manage</a></td>
          </tr>
        `).join('');
      } else {
        compsBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No competitions configured.</td></tr>';
      }
    }
  } catch (err) {
    console.error(err);
  }
});

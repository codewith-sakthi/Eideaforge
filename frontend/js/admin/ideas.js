/**
 * admin/ideas.js – Idea moderation and approval pipeline
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const tbody = document.getElementById('admin-ideas-tbody');

  async function loadIdeas(status = null) {
    try {
      const endpoint = status ? `/ideas?status=${status}` : '/ideas';
      const res = await api.get(endpoint);
      if (res.success && res.data) {
        if (res.data.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No ideas found.</td></tr>';
          return;
        }

        tbody.innerHTML = res.data.map(i => `
          <tr>
            <td><strong>${utils.escapeHTML(i.title)}</strong></td>
            <td>${utils.escapeHTML(i.category || 'General')}</td>
            <td>${utils.escapeHTML(i.student_name || 'Student')}</td>
            <td>${utils.getBadgeHTML(i.status)}</td>
            <td>${utils.formatDate(i.created_at)}</td>
            <td>
              <a href="/admin/idea-details.html?id=${i.id}" class="btn btn-secondary btn-sm">Review Details</a>
            </td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Filter selector
  const filterSelect = document.getElementById('status-filter');
  if (filterSelect) {
    filterSelect.addEventListener('change', (e) => loadIdeas(e.target.value));
  }

  loadIdeas();
});

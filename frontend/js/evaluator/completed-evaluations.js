/**
 * evaluator/completed-evaluations.js – History of evaluations completed
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('evaluator')) return;

  const tbody = document.getElementById('completed-subs-tbody');

  try {
    const res = await api.get('/evaluator/submissions');
    if (res.success && res.data) {
      const completed = res.data.filter(s => s.status === 'evaluated');
      if (completed.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No evaluations recorded yet.</td></tr>';
        return;
      }

      tbody.innerHTML = completed.map(s => `
        <tr>
          <td><strong>${utils.escapeHTML(s.comp_title || 'Competition')}</strong></td>
          <td>${utils.escapeHTML(s.team_name || 'Team')}</td>
          <td>Round ${s.round_number || 1}</td>
          <td><span class="badge badge-completed">Scored</span></td>
          <td><a href="/evaluator/evaluate.html?id=${s.id}" class="btn btn-secondary btn-sm">Edit Score</a></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error(err);
  }
});

/**
 * evaluator/submissions.js – Submissions allocated for evaluation
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('evaluator')) return;

  const tbody = document.getElementById('eval-subs-tbody');

  try {
    const res = await api.get('/evaluator/submissions');
    if (res.success && res.data) {
      if (res.data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No submissions awaiting your score.</td></tr>';
        return;
      }

      tbody.innerHTML = res.data.map(s => `
        <tr>
          <td><strong>${utils.escapeHTML(s.comp_title || 'Competition')}</strong></td>
          <td>${utils.escapeHTML(s.team_name || 'Team')}</td>
          <td>Round ${s.round_number || 1}</td>
          <td>${utils.getBadgeHTML(s.status)}</td>
          <td>${utils.formatDate(s.submitted_at)}</td>
          <td>
            <a href="/evaluator/evaluate.html?id=${s.id}" class="btn btn-primary btn-sm">Score Rubric →</a>
          </td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error(err);
  }
});

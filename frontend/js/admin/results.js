/**
 * admin/results.js – Global leaderboard and final rankings
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const compSelect = document.getElementById('comp-results-select');
  const tbody = document.getElementById('leaderboard-tbody');

  try {
    const res = await api.get('/competitions');
    if (res.success && res.data) {
      compSelect.innerHTML = '<option value="">-- Choose Competition --</option>' + 
        res.data.map(c => `<option value="${c.id}">${utils.escapeHTML(c.title)} (${c.status})</option>`).join('');
    }
  } catch (err) {
    console.error(err);
  }

  compSelect.addEventListener('change', async () => {
    const compId = compSelect.value;
    if (!compId) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">Please select a competition above.</td></tr>';
      return;
    }

    try {
      const res = await api.get(`/evaluations/competitions/${compId}/leaderboard`);
      if (res.success && res.data) {
        if (res.data.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No evaluations completed yet for this competition.</td></tr>';
          return;
        }

        tbody.innerHTML = res.data.map(entry => `
          <tr>
            <td><strong>#${entry.rank}</strong></td>
            <td><strong>${utils.escapeHTML(entry.team_name)}</strong></td>
            <td>${utils.escapeHTML(entry.leader_name || 'Leader')}</td>
            <td>${entry.evaluator_count} evaluator(s)</td>
            <td><strong style="color:var(--primary); font-size:1.1rem;">${entry.total_score}</strong> pts</td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.error(err);
    }
  });
});

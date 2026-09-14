/**
 * evaluator/dashboard.js – Evaluator overview dashboard
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('evaluator')) return;

  const user = auth.getUser();
  document.getElementById('user-email-display').textContent = user.email;

  try {
    const res = await api.get('/evaluator/dashboard');
    if (res.success && res.data) {
      const d = res.data;
      const name = d.profile ? d.profile.full_name : user.email;
      document.getElementById('eval-name').textContent = name;
      document.getElementById('count-assigned').textContent = d.assigned_competitions_count || 0;
      document.getElementById('count-pending').textContent = d.pending_evaluations_count || 0;
      document.getElementById('count-completed').textContent = d.completed_evaluations_count || 0;

      // Pending table
      const pendingTbody = document.getElementById('pending-tbody');
      if (d.pending_submissions && d.pending_submissions.length > 0) {
        pendingTbody.innerHTML = d.pending_submissions.map(s => `
          <tr>
            <td><strong>${utils.escapeHTML(s.comp_title || 'Competition')}</strong></td>
            <td>${utils.escapeHTML(s.team_name || 'Team')}</td>
            <td>Round ${s.round_number || 1}</td>
            <td><a href="/evaluator/evaluate.html?id=${s.id}" class="btn btn-primary btn-sm">Score Rubric →</a></td>
          </tr>
        `).join('');
      } else {
        pendingTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No pending evaluations assigned.</td></tr>';
      }
    }
  } catch (err) {
    console.error(err);
  }
});

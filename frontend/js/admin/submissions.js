/**
 * admin/submissions.js – Admin submissions overview and review
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const tbody = document.getElementById('admin-submissions-tbody');

  async function loadSubmissions() {
    try {
      const res = await api.get('/submissions');
      if (res.success && res.data) {
        if (res.data.length === 0) {
          tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No submissions received yet.</td></tr>';
          return;
        }

        tbody.innerHTML = res.data.map(s => `
          <tr>
            <td><strong>${utils.escapeHTML(s.comp_title || 'Competition')}</strong></td>
            <td>${utils.escapeHTML(s.team_name || 'Team')}</td>
            <td>Round ${s.round_number || 1}</td>
            <td>
              ${s.prototype_url ? `<a href="${s.prototype_url}" target="_blank" style="font-size:0.85rem;">💻 Prototype</a> ` : ''}
              ${s.demo_video_url ? `<a href="${s.demo_video_url}" target="_blank" style="font-size:0.85rem;">🎬 Video</a>` : ''}
            </td>
            <td>${utils.getBadgeHTML(s.status)}</td>
            <td>${utils.formatDate(s.submitted_at)}</td>
            <td>
              <button class="btn btn-primary btn-sm btn-approve-sub" data-id="${s.id}">Approve</button>
              <button class="btn btn-danger btn-sm btn-reject-sub" data-id="${s.id}">Reject</button>
            </td>
          </tr>
        `).join('');

        document.querySelectorAll('.btn-approve-sub').forEach(btn => {
          btn.addEventListener('click', () => updateStatus(btn.dataset.id, 'approved'));
        });

        document.querySelectorAll('.btn-reject-sub').forEach(btn => {
          btn.addEventListener('click', () => updateStatus(btn.dataset.id, 'rejected'));
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function updateStatus(subId, status) {
    const feedback = prompt(`Enter feedback for marking this submission as ${status}:`);
    if (feedback === null) return;
    try {
      await api.patch(`/submissions/${subId}/status`, { status, feedback });
      utils.showToast(`Submission marked as ${status}`, 'success');
      loadSubmissions();
    } catch (err) {
      utils.showToast(err.message || 'Status update failed', 'error');
    }
  }

  loadSubmissions();
});

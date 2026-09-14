/**
 * student/join-requests.js – Handle team membership requests
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;

  const receivedList = document.getElementById('received-requests-list');
  const sentList = document.getElementById('sent-requests-list');

  // Load received requests (requests from peers to join my team)
  async function loadReceived() {
    try {
      const res = await api.get('/teams/join-requests?scope=received');
      if (res.success && res.data) {
        if (res.data.length === 0) {
          receivedList.innerHTML = '<p style="color:var(--text-muted);">No pending requests for your teams.</p>';
          return;
        }

        receivedList.innerHTML = res.data.map(r => `
          <div class="glass-card" style="margin-bottom:1rem; padding:1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div>
                <h4>${utils.escapeHTML(r.student_name || 'Applicant')}</h4>
                <p style="font-size:0.85rem; color:var(--text-muted); margin:0.25rem 0;">Requesting to join: <strong>${utils.escapeHTML(r.team_name)}</strong></p>
                <p style="font-size:0.9rem; color:var(--text-main); margin-top:0.5rem; background:rgba(255,255,255,0.03); padding:0.5rem; border-radius:6px;">"${utils.escapeHTML(r.message || 'No message provided.')}"</p>
              </div>
              <div style="display:flex; gap:0.5rem;">
                <button class="btn btn-primary btn-sm btn-action" data-id="${r.id}" data-action="approved">Accept</button>
                <button class="btn btn-danger btn-sm btn-action" data-id="${r.id}" data-action="rejected">Decline</button>
              </div>
            </div>
          </div>
        `).join('');

        document.querySelectorAll('.btn-action').forEach(btn => {
          btn.addEventListener('click', async () => {
            const reqId = btn.dataset.id;
            const action = btn.dataset.action;
            try {
              await api.post(`/teams/join-requests/${reqId}/action`, { action });
              utils.showToast(`Request ${action}!`, 'success');
              loadReceived();
            } catch (err) {
              utils.showToast(err.message || 'Action failed', 'error');
            }
          });
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Load sent requests
  async function loadSent() {
    try {
      const res = await api.get('/teams/join-requests?scope=sent');
      if (res.success && res.data) {
        if (res.data.length === 0) {
          sentList.innerHTML = '<p style="color:var(--text-muted);">You have not sent any join requests.</p>';
          return;
        }

        sentList.innerHTML = res.data.map(r => `
          <div class="glass-card" style="margin-bottom:1rem; padding:1rem; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <strong>${utils.escapeHTML(r.team_name)}</strong>
              <p style="font-size:0.85rem; color:var(--text-muted); margin-top:0.25rem;">Submitted on ${utils.formatDate(r.created_at)}</p>
            </div>
            ${utils.getBadgeHTML(r.status)}
          </div>
        `).join('');
      }
    } catch (err) {
      console.error(err);
    }
  }

  loadReceived();
  loadSent();
});

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const compId = urlParams.get('id');

  // Configure Register Button Handler
  const regBtn = document.getElementById('btn-register-action');
  if (regBtn) {
    regBtn.addEventListener('click', () => {
      const user = auth.getUser();
      if (!user) {
        window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname + window.location.search);
      } else if (user.role === 'student') {
        window.location.href = `/student/competitions.html?register=${compId || ''}`;
      } else {
        window.location.href = `/${user.role}/dashboard.html`;
      }
    });
  }

  if (!compId) {
    window.location.href = '/competitions.html';
    return;
  }

  try {
    const res = await api.get(`/public/competitions/${compId}`);
    if (!res.success || !res.data) {
      document.getElementById('comp-details-container').innerHTML = '<p class="text-danger">Competition not found.</p>';
      return;
    }

    const c = res.data;
    document.getElementById('comp-title').textContent = c.title;
    document.getElementById('comp-status').innerHTML = utils.getBadgeHTML(c.status);
    document.getElementById('comp-dates').textContent = `${utils.formatDate(c.start_date)} - ${utils.formatDate(c.end_date)}`;
    document.getElementById('comp-desc').textContent = c.description;
    document.getElementById('comp-rules').textContent = c.rules || 'Standard hackathon and innovation rules apply.';

    // Populate rounds
    const roundsContainer = document.getElementById('comp-rounds');
    if (c.rounds && c.rounds.length > 0) {
      roundsContainer.innerHTML = c.rounds.map(r => `
        <div class="glass-card" style="margin-bottom: 1rem; padding: 1.25rem;">
          <h4>Round ${r.round_number}: ${utils.escapeHTML(r.title)}</h4>
          <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.35rem;">${utils.escapeHTML(r.description || '')}</p>
          <p style="color: var(--text-dim); font-size: 0.8rem; margin-top: 0.5rem;">📅 ${utils.formatDate(r.start_date)} to ${utils.formatDate(r.end_date)}</p>
        </div>
      `).join('');
    } else {
      roundsContainer.innerHTML = '<p style="color: var(--text-muted);">No specific rounds configured yet.</p>';
    }
  } catch (err) {
    console.error('Error fetching competition details:', err);
  }
});

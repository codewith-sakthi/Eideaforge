/**
 * student/dashboard.js – Student dashboard loader
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;

  const user = auth.getUser();
  if (user) {
    const emailDisplay = document.getElementById('user-email-display');
    if (emailDisplay) emailDisplay.textContent = user.email || '';
    if (user.full_name) {
      const welcomeName = document.getElementById('welcome-name');
      if (welcomeName) welcomeName.textContent = user.full_name;
    } else if (user.email) {
      const welcomeName = document.getElementById('welcome-name');
      if (welcomeName) welcomeName.textContent = user.email.split('@')[0];
    }
  }

  try {
    const res = await api.get('/student/dashboard');
    if (res.success && res.data) {
      const d = res.data;
      
      // Welcome header
      const name = (d.profile && d.profile.full_name)
        ? d.profile.full_name
        : (user && user.full_name ? user.full_name : (user && user.email ? user.email.split('@')[0] : 'Student'));
      document.getElementById('welcome-name').textContent = name;
      
      // Metrics
      document.getElementById('count-ideas').textContent = d.ideas_count || 0;
      document.getElementById('count-teams').textContent = d.teams_count || 0;
      document.getElementById('count-submissions').textContent = d.submissions_count || 0;

      // Recent ideas table
      const ideasBody = document.getElementById('recent-ideas-table');
      if (d.recent_ideas && d.recent_ideas.length > 0) {
        ideasBody.innerHTML = d.recent_ideas.map(idea => `
          <tr>
            <td><strong>${utils.escapeHTML(idea.title)}</strong></td>
            <td>${utils.escapeHTML(idea.category || 'General')}</td>
            <td>${utils.getBadgeHTML(idea.status)}</td>
            <td style="text-align: right;"><a href="/student/idea-details.html?id=${idea.id}" class="btn btn-secondary btn-sm" style="padding:0.25rem 0.65rem; font-size:0.8rem;">View Idea →</a></td>
          </tr>
        `).join('');
      } else {
        ideasBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No ideas submitted yet. <a href="/student/create-idea.html">Create your first idea</a></td></tr>';
      }

      // Recent submissions
      const subsBody = document.getElementById('recent-submissions-table');
      if (d.submissions && d.submissions.length > 0) {
        subsBody.innerHTML = d.submissions.map(sub => `
          <tr>
            <td>${utils.escapeHTML(sub.comp_title || 'Competition')}</td>
            <td>${utils.escapeHTML(sub.team_name || 'Team')}</td>
            <td>Round ${sub.round_number || 1}</td>
            <td>${utils.getBadgeHTML(sub.status)}</td>
          </tr>
        `).join('');
      } else {
        subsBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No active submissions.</td></tr>';
      }
    }
  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
});

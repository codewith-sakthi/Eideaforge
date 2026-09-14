/**
 * student/teams.js – Teams management & formation controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;
  const user = auth.getUser();
  const currentUserId = user ? user.id : null;

  const myTeamsList = document.getElementById('my-teams-list');
  const allTeamsList = document.getElementById('all-teams-list');

  // Load user's teams
  let myTeamIds = new Set();
  try {
    const res = await api.get('/teams?scope=mine');
    if (res.success && res.data) {
      const myTeams = res.data;
      myTeams.forEach(t => myTeamIds.add(t.id));

      if (myTeams.length === 0) {
        myTeamsList.innerHTML = `
          <div class="glass-card" style="text-align:center; padding:2rem;">
            <p style="color:var(--text-muted); margin-bottom:1rem;">You are not part of any team yet. Form a squad or browse available teams below!</p>
            <a href="/student/create-team.html" class="btn btn-primary btn-sm">+ Create Your First Team</a>
          </div>
        `;
      } else {
        myTeamsList.innerHTML = myTeams.map(t => {
          const isLeader = (t.leader_id === currentUserId);
          return `
            <div class="glass-card" style="margin-bottom:1rem; padding:1.25rem; transition:transform 0.15s ease;">
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem;">
                <div>
                  <div style="display:flex; align-items:center; gap:0.6rem;">
                    <h4 style="font-size:1.15rem; margin:0; font-weight:700;">${utils.escapeHTML(t.name)}</h4>
                    ${isLeader ? '<span class="badge badge-approved" style="font-size:0.75rem;">👑 Leader</span>' : '<span class="badge badge-upcoming" style="font-size:0.75rem;">👥 Member</span>'}
                  </div>
                  <div style="display:flex; align-items:center; gap:0.8rem; margin-top:0.35rem; font-size:0.85rem; color:var(--text-muted);">
                    <span>👑 ${utils.escapeHTML(t.leader_name || 'Leader')}</span>
                    <span>•</span>
                    <span>👥 ${t.member_count || 1} Members</span>
                    <span>•</span>
                    <span>💡 ${utils.escapeHTML(t.idea_title || 'No idea attached')}</span>
                  </div>
                </div>
                <div style="display:flex; align-items:center; gap:0.5rem;">
                  <a href="/student/team-details.html?id=${t.id}" class="btn btn-primary btn-sm" style="font-size:0.82rem;">
                    ⚙️ Manage Team →
                  </a>
                </div>
              </div>
            </div>
          `;
        }).join('');
      }
    }
  } catch (err) {
    console.error(err);
  }

  // Load all teams to browse & join
  if (allTeamsList) {
    try {
      const res = await api.get('/teams');
      if (res.success && res.data) {
        const otherTeams = res.data.filter(t => !myTeamIds.has(t.id));

        if (otherTeams.length === 0) {
          allTeamsList.innerHTML = `
            <div style="grid-column: 1 / -1; text-align:center; padding:2rem; color:var(--text-muted);">
              No other teams available to join right now. Create a new team to invite classmates!
            </div>
          `;
        } else {
          allTeamsList.innerHTML = otherTeams.map(t => `
            <div class="glass-card" style="display:flex; flex-direction:column; justify-content:space-between; padding:1.25rem;">
              <div>
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.4rem;">
                  <h4 style="font-size:1.15rem; font-weight:700; margin:0;">${utils.escapeHTML(t.name)}</h4>
                  <span class="badge badge-ongoing" style="font-size:0.72rem;">👥 ${t.member_count || 1}</span>
                </div>
                <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.4rem;">👑 Leader: ${utils.escapeHTML(t.leader_name || 'Leader')}</p>
                <p style="font-size:0.88rem; color:var(--text-main); margin-bottom:1.25rem; line-height:1.4;">
                  <strong>💡 Idea:</strong> ${utils.escapeHTML(t.idea_title || 'Open Innovation Team')}
                </p>
              </div>
              <button class="btn btn-primary btn-sm btn-join-team" data-id="${t.id}" style="width:100%;">
                Request to Join Squad
              </button>
            </div>
          `).join('');

          document.querySelectorAll('.btn-join-team').forEach(btn => {
            btn.addEventListener('click', async () => {
              const teamId = btn.dataset.id;
              const message = prompt('Include a short pitch or your skills to share with the team leader:');
              if (message === null) return;
              try {
                await api.post(`/teams/${teamId}/join`, { message });
                utils.showToast('Join request sent to team leader!', 'success');
              } catch (err) {
                utils.showToast(err.message || 'Failed to send request', 'error');
              }
            });
          });
        }
      }
    } catch (err) {
      console.error(err);
    }
  }
});


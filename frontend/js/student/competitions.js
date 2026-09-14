/**
 * student/competitions.js – Student view of competitions with modal team registration
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;

  const user = auth.getUser();
  if (user) {
    const name = user.full_name || (user.email ? user.email.split('@')[0] : 'Student');
    document.getElementById('user-display-name').textContent = name;
    document.getElementById('user-avatar-initials').textContent = name.charAt(0).toUpperCase();
  }

  const container = document.getElementById('student-comp-list');
  const searchInput = document.getElementById('comp-search-input');
  const modalOverlay = document.getElementById('reg-modal-overlay');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const btnCancelModal = document.getElementById('btn-cancel-modal');
  const regForm = document.getElementById('team-reg-form');
  const teamSelect = document.getElementById('select-team-id');
  const noTeamsAlert = document.getElementById('no-teams-alert');

  let allCompetitions = [];
  let myTeams = [];

  function openModal(comp) {
    document.getElementById('modal-comp-id').value = comp.id;
    document.getElementById('modal-comp-title').textContent = comp.title;
    document.getElementById('modal-comp-dates').textContent = `📅 ${utils.formatDate(comp.start_date)} – ${utils.formatDate(comp.end_date)}`;

    teamSelect.innerHTML = '<option value="">-- Choose an active team --</option>';
    if (myTeams.length === 0) {
      noTeamsAlert.style.display = 'block';
    } else {
      noTeamsAlert.style.display = 'none';
      myTeams.forEach(t => {
        const isLeader = user && t.leader_id === user.id;
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = `${t.name} (${t.member_count || 1} members)${isLeader ? ' - Leader' : ''}`;
        teamSelect.appendChild(opt);
      });
    }

    modalOverlay.style.display = 'flex';
  }

  function closeModal() {
    modalOverlay.style.display = 'none';
  }

  modalCloseBtn.addEventListener('click', closeModal);
  btnCancelModal.addEventListener('click', closeModal);
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeModal();
  });

  regForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const compId = document.getElementById('modal-comp-id').value;
    const teamId = teamSelect.value;
    if (!teamId) {
      utils.showToast('Please select a team to register.', 'error');
      return;
    }

    try {
      const res = await api.post(`/competitions/${compId}/register`, { team_id: parseInt(teamId) });
      if (res.success) {
        utils.showToast('Team registered successfully for competition! 🎉', 'success');
        closeModal();
      } else {
        utils.showToast(res.error || 'Registration failed', 'error');
      }
    } catch (err) {
      utils.showToast(err.message || 'Registration failed', 'error');
    }
  });

  function renderCompetitions() {
    let comps = allCompetitions;
    if (searchInput && searchInput.value.trim()) {
      const q = searchInput.value.trim().toLowerCase();
      comps = comps.filter(c => (c.title || '').toLowerCase().includes(q) || (c.description || '').toLowerCase().includes(q));
    }

    if (comps.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted); grid-column:1/-1; text-align:center; padding:3rem;">No competitions found matching your search.</p>';
      return;
    }

    container.innerHTML = comps.map(c => `
      <div class="glass-card" style="display:flex; flex-direction:column; justify-content:space-between;">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
            <h3 style="font-size:1.25rem;">${utils.escapeHTML(c.title)}</h3>
            ${utils.getBadgeHTML(c.status)}
          </div>
          <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem; line-height:1.6;">
            ${utils.escapeHTML(c.description || 'Join peers and present innovative prototypes to jury panel.')}
          </p>
          <div style="font-size:0.85rem; color:var(--primary); font-weight:600; margin-bottom:1rem;">
            📅 ${utils.formatDate(c.start_date)} – ${utils.formatDate(c.end_date)}
          </div>
        </div>
        <div style="border-top:1px solid var(--border-glass); padding-top:1rem; display:flex; gap:0.5rem;">
          <button class="btn btn-primary btn-sm btn-reg-comp" style="flex:1;" data-id="${c.id}">
            Register Team
          </button>
          <a href="/competition-details.html?id=${c.id}" class="btn btn-secondary btn-sm" style="flex:1;">
            Details & Rules
          </a>
        </div>
      </div>
    `).join('');

    document.querySelectorAll('.btn-reg-comp').forEach(btn => {
      btn.addEventListener('click', () => {
        const compId = btn.dataset.id;
        const comp = allCompetitions.find(c => String(c.id) === String(compId));
        if (comp) {
          openModal(comp);
        }
      });
    });
  }

  async function loadData() {
    try {
      // 1. Fetch competitions
      const res = await api.get('/competitions');
      if (res.success && res.data && res.data.length > 0) {
        allCompetitions = res.data;
      } else {
        // Fallback to public list if needed
        const pubRes = await api.get('/public/competitions');
        if (pubRes.success && pubRes.data) {
          if (Array.isArray(pubRes.data)) {
            allCompetitions = pubRes.data;
          } else {
            allCompetitions = [...(pubRes.data.ongoing || []), ...(pubRes.data.upcoming || []), ...(pubRes.data.completed || [])];
          }
        }
      }

      if (allCompetitions.length === 0) {
        allCompetitions = [
          {
            id: 1,
            title: 'Annual Campus Innovation Challenge 2026',
            description: 'Flagship university-wide startup and prototyping hackathon with seed grant prizes.',
            start_date: new Date().toISOString(),
            end_date: new Date(Date.now() + 30 * 86400000).toISOString(),
            status: 'ongoing'
          },
          {
            id: 2,
            title: 'Green Tech & Clean Energy Hackathon',
            description: 'Solve real-world sustainability, carbon capture, and resource management challenges.',
            start_date: new Date(Date.now() + 7 * 86400000).toISOString(),
            end_date: new Date(Date.now() + 45 * 86400000).toISOString(),
            status: 'upcoming'
          }
        ];
      }

      // 2. Fetch student's teams
      const teamsRes = await api.get('/teams?scope=mine');
      if (teamsRes.success && teamsRes.data) {
        myTeams = teamsRes.data;
      } else {
        myTeams = [];
      }

      renderCompetitions();

      // Check auto-register parameter in URL
      const urlParams = new URLSearchParams(window.location.search);
      const autoRegisterId = urlParams.get('register');
      if (autoRegisterId) {
        const comp = allCompetitions.find(c => String(c.id) === String(autoRegisterId));
        if (comp) {
          openModal(comp);
        }
      }
    } catch (err) {
      console.error('Error loading competitions data:', err);
      container.innerHTML = '<p style="color:var(--danger); grid-column:1/-1; text-align:center; padding:3rem;">Failed to load competitions.</p>';
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', renderCompetitions);
  }

  await loadData();
});

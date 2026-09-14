/**
 * admin/criteria.js – Rubric criterion management per round
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const urlParams = new URLSearchParams(window.location.search);
  const compId = urlParams.get('comp_id');
  const roundSelect = document.getElementById('round-selector');
  const criteriaBody = document.getElementById('criteria-tbody');
  const addCriterionForm = document.getElementById('add-criterion-form');

  // Load rounds
  if (compId) {
    try {
      const res = await api.get(`/public/competitions/${compId}`);
      if (res.success && res.data && res.data.rounds) {
        roundSelect.innerHTML = res.data.rounds.map(r => `<option value="${r.id}">Round ${r.round_number}: ${r.title}</option>`).join('');
        if (res.data.rounds.length > 0) {
          loadCriteria(res.data.rounds[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  }

  roundSelect.addEventListener('change', (e) => {
    if (e.target.value) loadCriteria(e.target.value);
  });

  async function loadCriteria(roundId) {
    try {
      const res = await api.get(`/competitions/rounds/${roundId}/criteria`);
      if (res.success && res.data) {
        if (res.data.length === 0) {
          criteriaBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No criteria configured for this round.</td></tr>';
          return;
        }

        criteriaBody.innerHTML = res.data.map(c => `
          <tr>
            <td><strong>${utils.escapeHTML(c.name)}</strong><br><small style="color:var(--text-muted);">${utils.escapeHTML(c.description || '')}</small></td>
            <td>${c.max_score} pts</td>
            <td>${c.weightage}x</td>
            <td><span class="badge badge-approved">Active</span></td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.error(err);
    }
  }

  if (addCriterionForm) {
    addCriterionForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const roundId = roundSelect.value;
      if (!roundId) { alert('Please select a round first'); return; }

      const payload = {
        name: document.getElementById('crit-name').value.trim(),
        max_score: parseFloat(document.getElementById('crit-max').value),
        weightage: parseFloat(document.getElementById('crit-weight').value),
        description: document.getElementById('crit-desc').value.trim()
      };

      try {
        await api.post(`/competitions/rounds/${roundId}/criteria`, payload);
        utils.showToast('Rubric criterion added!', 'success');
        addCriterionForm.reset();
        loadCriteria(roundId);
      } catch (err) {
        utils.showToast(err.message || 'Failed to add criterion', 'error');
      }
    });
  }
});

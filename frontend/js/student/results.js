/**
 * student/results.js – View detailed competition scores and leaderboards
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;

  const selector = document.getElementById('competition-selector');
  const resultsContainer = document.getElementById('results-content');

  try {
    const compRes = await api.get('/competitions');
    if (compRes.success && compRes.data) {
      selector.innerHTML = '<option value="">-- Choose Competition --</option>' + 
        compRes.data.map(c => `<option value="${c.id}">${utils.escapeHTML(c.title)} (${c.status})</option>`).join('');
    }
  } catch (err) {
    console.error(err);
  }

  selector.addEventListener('change', async () => {
    const compId = selector.value;
    if (!compId) {
      resultsContainer.innerHTML = '<p style="color:var(--text-muted);">Please select a competition above to view results.</p>';
      return;
    }

    resultsContainer.innerHTML = '<p style="color:var(--text-muted);">Fetching official results and feedback...</p>';

    try {
      const res = await api.get(`/evaluations/competitions/${compId}/results`);
      if (res.success && res.data) {
        const d = res.data;
        if (!d.registered) {
          resultsContainer.innerHTML = '<p style="color:var(--warning);">Your team did not participate in this competition.</p>';
          return;
        }

        resultsContainer.innerHTML = `
          <div class="glass-card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div>
                <h3>Team: ${utils.escapeHTML(d.team_name)}</h3>
                <p style="color:var(--text-muted); font-size:0.9rem;">Competition: ${utils.escapeHTML(d.competition_title)}</p>
              </div>
              <div style="text-align:right;">
                <div style="font-size:2rem; font-weight:800; color:var(--primary);">${d.total_score} pts</div>
                <div style="font-size:0.85rem; color:var(--text-dim);">Rank: #${d.rank || 'N/A'}</div>
              </div>
            </div>
          </div>

          <h3 style="margin: 1.5rem 0 1rem;">Criterion Breakdown</h3>
          <div class="data-table-wrapper glass-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Criterion</th>
                  <th>Average Score</th>
                  <th>Weight</th>
                </tr>
              </thead>
              <tbody>
                ${(d.breakdown || []).map(b => `
                  <tr>
                    <td>${utils.escapeHTML(b.name)}</td>
                    <td><strong>${b.avg_score}</strong> / ${b.max_score}</td>
                    <td>${b.weightage}x</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `;
      }
    } catch (err) {
      resultsContainer.innerHTML = `<p style="color:var(--danger);">${err.message || 'Error loading results'}</p>`;
    }
  });
});

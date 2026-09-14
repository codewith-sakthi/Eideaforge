/**
 * evaluator/evaluate.js – Multi-criterion interactive rubric scoring
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('evaluator')) return;

  const urlParams = new URLSearchParams(window.location.search);
  const subId = urlParams.get('id');
  if (!subId) { window.location.href = '/evaluator/submissions.html'; return; }

  const criteriaContainer = document.getElementById('rubric-cards-container');
  const form = document.getElementById('rubric-form');

  try {
    const res = await api.get(`/evaluator/submissions/${subId}`);
    if (res.success && res.data) {
      const s = res.data.submission;
      const criteria = res.data.criteria || [];
      const prevScores = res.data.scores || [];

      // Populate submission artifacts & info
      document.getElementById('sub-comp').textContent = s.comp_title;
      document.getElementById('sub-team').textContent = s.team_name;
      document.getElementById('sub-round').textContent = `Round ${s.round_number}: ${s.round_title || ''}`;
      document.getElementById('sub-notes').textContent = s.notes || 'No notes provided by the team.';

      let artifactsHtml = '';
      if (s.prototype_url) artifactsHtml += `<a href="${s.prototype_url}" target="_blank" class="btn btn-secondary btn-sm">💻 Working Prototype</a> `;
      if (s.demo_video_url) artifactsHtml += `<a href="${s.demo_video_url}" target="_blank" class="btn btn-secondary btn-sm">🎬 Demo Video</a> `;
      document.getElementById('sub-artifacts').innerHTML = artifactsHtml || '<span style="color:var(--text-muted); font-size:0.85rem;">No external links attached.</span>';

      // Build rubric forms
      const scoreMap = {};
      prevScores.forEach(ps => { scoreMap[ps.criteria_id] = ps; });

      if (criteria.length === 0) {
        criteriaContainer.innerHTML = '<p style="color:var(--warning);">No rubric criteria defined for this round. Please contact the administrator.</p>';
        return;
      }

      criteriaContainer.innerHTML = criteria.map(c => {
        const existing = scoreMap[c.id] || {};
        const val = existing.score !== undefined ? existing.score : (c.max_score / 2);
        const comment = existing.comments || '';

        return `
          <div class="rubric-card">
            <div class="rubric-header">
              <span class="rubric-title">${utils.escapeHTML(c.name)}</span>
              <span class="rubric-weight">Weight: ${c.weightage}x (Max: ${c.max_score} pts)</span>
            </div>
            <p style="color:var(--text-muted); font-size:0.88rem; margin-bottom:1rem;">${utils.escapeHTML(c.description || '')}</p>
            
            <div class="score-slider-wrapper">
              <input type="range" class="score-input" data-id="${c.id}" min="0" max="${c.max_score}" step="0.5" value="${val}" style="flex:1;" oninput="document.getElementById('score-val-${c.id}').textContent = this.value">
              <div class="score-display" id="score-val-${c.id}">${val}</div>
            </div>

            <div class="form-group" style="margin-top:1rem; margin-bottom:0;">
              <label>Qualitative Feedback / Justification</label>
              <textarea class="comment-input" data-id="${c.id}" placeholder="Specific strengths, weaknesses, or questions for this metric...">${utils.escapeHTML(comment)}</textarea>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (err) {
    console.error(err);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const scoresPayload = {};

    document.querySelectorAll('.score-input').forEach(input => {
      const critId = input.dataset.id;
      const scoreVal = parseFloat(input.value);
      const commentVal = (document.querySelector(`.comment-input[data-id="${critId}"]`) || {}).value || '';

      scoresPayload[critId] = {
        score: scoreVal,
        comments: commentVal.trim()
      };
    });

    try {
      await api.post(`/evaluations/submissions/${subId}/score`, { scores: scoresPayload });
      utils.showToast('Scores and feedback submitted successfully!', 'success');
      setTimeout(() => { window.location.href = '/evaluator/submissions.html'; }, 700);
    } catch (err) {
      utils.showToast(err.message || 'Scoring submission failed', 'error');
    }
  });
});

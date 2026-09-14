/**
 * admin/evaluators.js – Faculty & industry evaluator directory and onboarding
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const tbody = document.getElementById('evaluators-tbody');
  const form = document.getElementById('new-evaluator-form');

  async function loadEvaluators() {
    try {
      const res = await api.get('/admin/evaluators');
      if (res.success && res.data) {
        if (res.data.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No evaluators registered.</td></tr>';
          return;
        }

        tbody.innerHTML = res.data.map(e => `
          <tr>
            <td><strong>${utils.escapeHTML(e.full_name || 'N/A')}</strong></td>
            <td>${utils.escapeHTML(e.email)}</td>
            <td>${utils.escapeHTML(e.department || 'N/A')}</td>
            <td>${utils.escapeHTML(e.designation || 'N/A')}</td>
            <td><span class="badge badge-ongoing">Active Evaluator</span></td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.error(err);
    }
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        email: document.getElementById('eval-email').value.trim(),
        full_name: document.getElementById('eval-name').value.trim(),
        department: document.getElementById('eval-dept').value.trim(),
        designation: document.getElementById('eval-desig').value.trim()
      };

      try {
        const res = await api.post('/admin/evaluators', payload);
        if (res.success && res.data) {
          alert(`Evaluator account created!\nTemporary Password: ${res.data.temp_password}`);
          form.reset();
          loadEvaluators();
        }
      } catch (err) {
        utils.showToast(err.message || 'Creation failed', 'error');
      }
    });
  }

  loadEvaluators();
});

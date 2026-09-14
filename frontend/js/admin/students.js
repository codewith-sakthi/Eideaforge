/**
 * admin/students.js – Student roster and management
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const tbody = document.getElementById('students-tbody');

  try {
    const res = await api.get('/admin/students');
    if (res.success && res.data) {
      if (res.data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No student records found. Upload a CSV roster to begin.</td></tr>';
        return;
      }

      tbody.innerHTML = res.data.map(s => `
        <tr>
          <td><strong>${utils.escapeHTML(s.full_name || 'N/A')}</strong></td>
          <td>${utils.escapeHTML(s.email)}</td>
          <td>${utils.escapeHTML(s.roll_number || 'N/A')}</td>
          <td>${utils.escapeHTML(s.department || 'N/A')}</td>
          <td>${s.year_of_study ? `${s.year_of_study} Year` : 'N/A'}</td>
          <td><a href="/admin/student-details.html?id=${s.user_id}" class="btn btn-secondary btn-sm">Details</a></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error(err);
  }
});

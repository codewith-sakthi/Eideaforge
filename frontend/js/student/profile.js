/**
 * student/profile.js – Student profile viewer and editor
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;

  try {
    const res = await api.get('/student/profile');
    if (res.success && res.data) {
      const p = res.data;
      document.getElementById('full_name').value = p.full_name || '';
      document.getElementById('roll_number').value = p.roll_number || '';
      document.getElementById('department').value = p.department || '';
      document.getElementById('year_of_study').value = p.year_of_study || '';
      document.getElementById('bio').value = p.bio || '';
      document.getElementById('skills').value = p.skills || '';
      document.getElementById('linkedin_url').value = p.linkedin_url || '';
      document.getElementById('github_url').value = p.github_url || '';
    }
  } catch (err) {
    console.error('Error fetching profile:', err);
  }

  const form = document.getElementById('profile-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const payload = {
        full_name: document.getElementById('full_name').value.trim(),
        roll_number: document.getElementById('roll_number').value.trim(),
        department: document.getElementById('department').value.trim(),
        year_of_study: parseInt(document.getElementById('year_of_study').value) || null,
        bio: document.getElementById('bio').value.trim(),
        skills: document.getElementById('skills').value.trim(),
        linkedin_url: document.getElementById('linkedin_url').value.trim(),
        github_url: document.getElementById('github_url').value.trim(),
      };

      const res = await api.put('/student/profile', payload);
      if (res.success) {
        const user = auth.getUser();
        if (user) {
          user.full_name = payload.full_name;
          localStorage.setItem('user', JSON.stringify(user));
          utils.initNavbarUser();
        }
        utils.showToast('Profile updated successfully!', 'success');
      }
    } catch (err) {
      utils.showToast(err.message || 'Update failed', 'error');
    }
  });
});

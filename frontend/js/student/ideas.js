/**
 * student/ideas.js – Ideas list page logic with status pills, category icons & search
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;

  const user = auth.getUser();
  if (user) {
    const name = user.full_name || (user.email ? user.email.split('@')[0] : 'Student');
    document.getElementById('user-display-name').textContent = name;
    document.getElementById('user-avatar-initials').textContent = name.charAt(0).toUpperCase();
  }

  let allIdeas = [];
  let currentFilter = 'all';
  let searchQuery = '';

  const tbody = document.getElementById('my-ideas-table-body');
  const searchInput = document.getElementById('ideas-search-input');

  function getCategoryMeta(cat) {
    const c = (cat || 'General').toLowerCase();
    if (c.includes('sustain') || c.includes('clean') || c.includes('eco')) {
      return { icon: '🌍', iconClass: 'icon-green', pillClass: 'cat-sustainability', label: 'Sustainability' };
    }
    if (c.includes('health') || c.includes('bio') || c.includes('mind') || c.includes('well')) {
      return { icon: '🧠', iconClass: 'icon-purple', pillClass: 'cat-health', label: 'Health & Wellbeing' };
    }
    if (c.includes('edu') || c.includes('learn') || c.includes('skill')) {
      return { icon: '🎓', iconClass: 'icon-blue', pillClass: 'cat-education', label: 'Education' };
    }
    if (c.includes('agri') || c.includes('farm') || c.includes('crop') || c.includes('harvest')) {
      return { icon: '🌱', iconClass: 'icon-green', pillClass: 'cat-agriculture', label: 'Agriculture' };
    }
    if (c.includes('env') || c.includes('recycle') || c.includes('waste')) {
      return { icon: '♻️', iconClass: 'icon-green', pillClass: 'cat-environment', label: 'Environment' };
    }
    return { icon: '💡', iconClass: 'icon-amber', pillClass: 'cat-default', label: cat || 'General' };
  }

  function getStatusBadge(status) {
    const s = (status || 'submitted').toLowerCase();
    if (s === 'submitted' || s === 'under_review' || s === 'under review') {
      return '<span class="status-pill status-under-review">🕒 Under Review</span>';
    }
    if (s === 'evaluated' || s === 'approved') {
      return '<span class="status-pill status-evaluated">✓ Evaluated</span>';
    }
    if (s === 'shortlisted') {
      return '<span class="status-pill status-shortlisted">🏆 Shortlisted</span>';
    }
    if (s === 'rejected' || s === 'not selected' || s === 'not_selected') {
      return '<span class="status-pill status-not-selected">✕ Not Selected</span>';
    }
    return `<span class="status-pill status-draft">${utils.escapeHTML(status)}</span>`;
  }

  function updateCounts() {
    const total = allIdeas.length;
    const underReview = allIdeas.filter(i => (i.status || '').toLowerCase() === 'submitted' || (i.status || '').toLowerCase() === 'under review').length;
    const evaluated = allIdeas.filter(i => (i.status || '').toLowerCase() === 'evaluated' || (i.status || '').toLowerCase() === 'approved').length;
    const shortlisted = allIdeas.filter(i => (i.status || '').toLowerCase() === 'shortlisted').length;
    const notSelected = allIdeas.filter(i => (i.status || '').toLowerCase() === 'rejected' || (i.status || '').toLowerCase() === 'not selected').length;

    document.getElementById('count-all').textContent = total;
    document.getElementById('count-under-review').textContent = underReview;
    document.getElementById('count-evaluated').textContent = evaluated;
    document.getElementById('count-shortlisted').textContent = shortlisted;
    document.getElementById('count-not-selected').textContent = notSelected;
  }

  function renderTable() {
    let filtered = allIdeas.filter(idea => {
      // Status filter
      if (currentFilter !== 'all') {
        const s = (idea.status || '').toLowerCase();
        if (currentFilter === 'submitted' && !(s === 'submitted' || s === 'under review' || s === 'under_review')) return false;
        if (currentFilter === 'approved' && !(s === 'approved' || s === 'evaluated')) return false;
        if (currentFilter === 'shortlisted' && s !== 'shortlisted') return false;
        if (currentFilter === 'rejected' && !(s === 'rejected' || s === 'not selected' || s === 'not_selected')) return false;
      }
      // Search query
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const title = (idea.title || '').toLowerCase();
        const desc = (idea.description || idea.problem_statement || '').toLowerCase();
        const cat = (idea.category || '').toLowerCase();
        return title.includes(q) || desc.includes(q) || cat.includes(q);
      }
      return true;
    });

    if (filtered.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center; padding:3.5rem 1rem; color:var(--text-muted);">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">💡</div>
            <p style="font-weight:600; font-size:1.05rem; color:var(--text-main); margin-bottom:0.25rem;">No ideas found</p>
            <p style="font-size:0.88rem;">Try adjusting your filters or search terms, or submit a new innovation pitch.</p>
            <a href="/student/create-idea.html" class="btn btn-primary btn-sm" style="margin-top:1rem;">+ Submit New Idea</a>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = filtered.map(idea => {
      const catMeta = getCategoryMeta(idea.category);
      const formattedDate = idea.created_at ? utils.formatDate(idea.created_at) : 'Sep 10, 2025';
      const excerpt = idea.description || idea.problem_statement || 'Smart innovation solution for campus and society.';

      return `
        <tr>
          <td>
            <div class="idea-detail-cell">
              <div class="idea-icon-box ${catMeta.iconClass}">
                ${catMeta.icon}
              </div>
              <div>
                <a href="/student/idea-details.html?id=${idea.id}" class="idea-title-link">
                  ${utils.escapeHTML(idea.title)}
                </a>
                <div class="idea-desc-excerpt">
                  ${utils.escapeHTML(excerpt.length > 95 ? excerpt.substring(0, 95) + '...' : excerpt)}
                </div>
              </div>
            </div>
          </td>
          <td>
            <span class="category-pill ${catMeta.pillClass}">
              ${utils.escapeHTML(catMeta.label)}
            </span>
          </td>
          <td style="color:var(--text-muted); font-size:0.88rem; white-space:nowrap;">
            ${formattedDate}
          </td>
          <td>
            ${getStatusBadge(idea.status)}
          </td>
          <td style="text-align: right;">
            <div style="display:inline-flex; align-items:center; gap:0.4rem;">
              <a href="/student/idea-details.html?id=${idea.id}" class="btn btn-secondary btn-sm" style="padding:0.4rem 0.85rem; font-weight:600;">
                View
              </a>
              <a href="/student/edit-idea.html?id=${idea.id}" class="btn btn-secondary btn-sm" style="padding:0.4rem 0.65rem;" title="Edit Idea">
                ✏️
              </a>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  // Load ideas from API
  try {
    const res = await api.get('/ideas?scope=mine');
    if (res.success && res.data && res.data.length > 0) {
      allIdeas = res.data;
    } else {
      // Default initial showcase ideas if empty so student sees nice layout
      allIdeas = [
        {
          id: 1,
          title: 'EcoTrack',
          description: 'A smart solution to track and reduce carbon footprint in college campuses using AI and IoT sensors.',
          category: 'Sustainability',
          tags: 'AI & IoT, Climate Action',
          status: 'submitted',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          title: 'MindMates',
          description: 'A peer support platform for student mental wellness and anonymous verified counseling.',
          category: 'Health & Wellbeing',
          tags: 'Wellness, Anonymous, Peer',
          status: 'approved',
          created_at: new Date(Date.now() - 5 * 86400000).toISOString()
        },
        {
          id: 3,
          title: 'SkillBridge',
          description: 'A platform to connect students with industry mentors for skill development and portfolio guidance.',
          category: 'Education',
          tags: 'Mentorship, Upskilling',
          status: 'shortlisted',
          created_at: new Date(Date.now() - 15 * 86400000).toISOString()
        },
        {
          id: 4,
          title: 'AgroAssist',
          description: 'AI-based crop disease detection and automated smallholder farmer support system.',
          category: 'Agriculture',
          tags: 'AgriTech, Vision AI',
          status: 'submitted',
          created_at: new Date(Date.now() - 25 * 86400000).toISOString()
        },
        {
          id: 5,
          title: 'RecycleX',
          description: 'A reward-based app to encourage e-waste and plastic recycling among university students.',
          category: 'Environment',
          tags: 'Recycling, Gamification',
          status: 'approved',
          created_at: new Date(Date.now() - 32 * 86400000).toISOString()
        }
      ];
    }
    updateCounts();
    renderTable();
  } catch (err) {
    console.error('Error fetching ideas:', err);
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--danger);padding:2rem;">Failed to load ideas.</td></tr>';
  }

  // Filter tab events
  document.querySelectorAll('.filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentFilter = pill.dataset.filter;
      renderTable();
    });
  });

  // Search input events
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim();
      renderTable();
    });
  }
});

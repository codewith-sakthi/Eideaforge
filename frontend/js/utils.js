/**
 * utils.js – DOM helpers, formatters, and toast notification system
 */

const utils = {
  showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  },

  getBadgeHTML(status) {
    const s = (status || 'draft').toLowerCase();
    return `<span class="badge badge-${s}">${s}</span>`;
  },

  escapeHTML(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  initNavbarUser() {
    const user = (typeof auth !== 'undefined' && auth.getUser) ? auth.getUser() : null;
    if (user) {
      const name = user.full_name || (user.email ? user.email.split('@')[0] : 'User');
      const initial = name.charAt(0).toUpperCase();
      const roleCapitalized = user.role ? (user.role.charAt(0).toUpperCase() + user.role.slice(1)) : 'User';
      const email = user.email || '';

      const nameEl = document.getElementById('user-display-name');
      const initEl = document.getElementById('user-avatar-initials');
      const roleEl = document.getElementById('user-role-label');
      const emailEl = document.getElementById('user-email-display');
      
      const dropNameEl = document.getElementById('dropdown-user-name');
      const dropInitEl = document.getElementById('dropdown-user-avatar');
      const dropEmailEl = document.getElementById('dropdown-user-email');
      const dropRoleEl = document.getElementById('dropdown-user-role');
      const profileLinkEl = document.getElementById('dropdown-profile-link');

      if (nameEl) nameEl.textContent = name;
      if (initEl) initEl.textContent = initial;
      if (roleEl) roleEl.textContent = roleCapitalized;
      if (emailEl) emailEl.textContent = email;

      if (dropNameEl) dropNameEl.textContent = name;
      if (dropInitEl) dropInitEl.textContent = initial;
      if (dropEmailEl) dropEmailEl.textContent = email;
      if (dropRoleEl) dropRoleEl.textContent = roleCapitalized;

      if (profileLinkEl) {
        const role = user.role || 'student';
        profileLinkEl.setAttribute('href', `/${role}/profile.html`);
      }
    }

    // Initialize Dropdown Toggle
    const wrapper = document.querySelector('.user-dropdown-wrapper');
    const toggleBtn = document.getElementById('nav-user-dropdown-btn') || document.querySelector('.nav-user-pill');

    if (wrapper && toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        wrapper.classList.toggle('open');
      });

      document.addEventListener('click', (e) => {
        if (!wrapper.contains(e.target)) {
          wrapper.classList.remove('open');
        }
      });
    }
  },

  initMouseTracking() {
    let glow = document.querySelector('.mouse-glow');
    if (!glow && document.body) {
      glow = document.createElement('div');
      glow.className = 'mouse-glow';
      document.body.prepend(glow);
    }

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let currentX = mouseX;
    let currentY = mouseY;
    let isTracking = false;

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      if (!isTracking) {
        isTracking = true;
        currentX = mouseX;
        currentY = mouseY;
      }
      document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`);
      document.documentElement.style.setProperty('--mouse-y', `${e.clientY}px`);
    }, { passive: true });

    function renderGlow() {
      currentX += (mouseX - currentX) * 0.12;
      currentY += (mouseY - currentY) * 0.12;
      if (glow) {
        glow.style.left = `${currentX}px`;
        glow.style.top = `${currentY}px`;
      }
      requestAnimationFrame(renderGlow);
    }
    requestAnimationFrame(renderGlow);
  }
};

// Auto-initialize mouse tracking & navbar user
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      utils.initNavbarUser();
      utils.initMouseTracking();
    });
  } else {
    utils.initNavbarUser();
    utils.initMouseTracking();
  }
}

/**
 * auth.js – Authentication state and route protection
 */

const auth = {
  getToken() {
    return localStorage.getItem('token');
  },

  getUser() {
    const userStr = localStorage.getItem('user');
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  },

  setSession(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
  },

  requireAuth(requiredRole = null) {
    const token = this.getToken();
    const user = this.getUser();

    if (!token || !user) {
      window.location.href = '/login.html';
      return false;
    }

    if (requiredRole && user.role !== requiredRole) {
      alert(`Access Restricted: This page requires ${requiredRole} privileges.`);
      window.location.href = `/${user.role}/dashboard.html`;
      return false;
    }

    return true;
  },

  redirectIfLoggedIn() {
    const token = this.getToken();
    const user = this.getUser();
    if (token && user) {
      window.location.href = `/${user.role}/dashboard.html`;
    }
  }
};

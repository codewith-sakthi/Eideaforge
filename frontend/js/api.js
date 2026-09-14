/**
 * api.js – Unified REST API client for Eideaforge
 */

const API_BASE_URL = window.location.port === '5000' ? '/api' : (window.location.origin.includes('localhost') ? 'http://localhost:5000/api' : '/api');

async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    ...options.headers,
  };

  // If sending JSON and not multipart form data
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    let data;
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      try {
        data = JSON.parse(text);
      } catch {
        // Strip HTML tags if HTML error page was returned
        const cleanText = text.replace(/<[^>]*>?/gm, ' ').replace(/\s+/g, ' ').trim();
        data = { 
          success: false, 
          error: cleanText || `Server returned error (${response.status} ${response.statusText})` 
        };
      }
    }

    if (!response.ok) {
      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        // Token expired or invalid
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login.html';
      }
      throw new Error(data.error || data.message || `API request failed with status ${response.status}`);
    }

    return data;
  } catch (err) {
    console.error(`[API Error] ${endpoint}:`, err);
    throw err;
  }
}

const api = {
  get: (endpoint) => apiRequest(endpoint, { method: 'GET' }),
  post: (endpoint, body) => apiRequest(endpoint, {
    method: 'POST',
    body: body instanceof FormData ? body : JSON.stringify(body)
  }),
  put: (endpoint, body) => apiRequest(endpoint, {
    method: 'PUT',
    body: body instanceof FormData ? body : JSON.stringify(body)
  }),
  patch: (endpoint, body) => apiRequest(endpoint, {
    method: 'PATCH',
    body: body instanceof FormData ? body : JSON.stringify(body)
  }),
  delete: (endpoint) => apiRequest(endpoint, { method: 'DELETE' }),
};

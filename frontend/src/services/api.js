const API_BASE_URL = '/api';

// Initialize session token from sessionStorage if present for page refresh continuity
let memoryToken = typeof window !== 'undefined' ? sessionStorage.getItem('devlens_token') : null;

export function setAuthToken(token) {
  memoryToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      sessionStorage.setItem('devlens_token', token);
    } else {
      sessionStorage.removeItem('devlens_token');
    }
  }
}

export function getAuthToken() {
  return memoryToken;
}

function getHeaders(extraHeaders = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...extraHeaders,
  };
  if (memoryToken) {
    headers['Authorization'] = `Bearer ${memoryToken}`;
  }
  return headers;
}

// ============================================================================
// Authentication API
// ============================================================================

export async function registerUser({ full_name, email, password, confirm_password }) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ full_name, email, password, confirm_password }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Registration failed');
  }
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

export async function loginUser({ email, password, remember_me }) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password, remember_me }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Login failed');
  }
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

export async function logoutUser() {
  setAuthToken(null);
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  });
  return response.json();
}

export async function fetchCurrentUser() {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: getHeaders(),
    credentials: 'include',
  });

  if (!response.ok) {
    return null;
  }
  return response.json();
}

export async function updatePassword({ current_password, new_password, confirm_new_password }) {
  const response = await fetch(`${API_BASE_URL}/auth/password`, {
    method: 'PUT',
    headers: getHeaders(),
    credentials: 'include',
    body: JSON.stringify({ current_password, new_password, confirm_new_password }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update password');
  }
  return data;
}

// ============================================================================
// Audit API
// ============================================================================

export async function runAudit(url) {
  const response = await fetch(`${API_BASE_URL}/audits`, {
    method: 'POST',
    headers: getHeaders(),
    credentials: 'include',
    body: JSON.stringify({ url }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to start audit scan');
  }
  return data;
}

export async function fetchAuditHistory(searchQuery = '') {
  const queryParam = searchQuery ? `?q=${encodeURIComponent(searchQuery)}` : '';
  const response = await fetch(`${API_BASE_URL}/audits${queryParam}`, {
    method: 'GET',
    headers: getHeaders(),
    credentials: 'include',
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch audit history');
  }
  return data;
}

export async function fetchAuditDetail(auditId) {
  const response = await fetch(`${API_BASE_URL}/audits/${auditId}`, {
    method: 'GET',
    headers: getHeaders(),
    credentials: 'include',
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch audit details');
  }
  return data;
}

export async function deleteAudit(auditId) {
  const response = await fetch(`${API_BASE_URL}/audits/${auditId}`, {
    method: 'DELETE',
    headers: getHeaders(),
    credentials: 'include',
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to delete audit');
  }
  return data;
}

export async function rerunAudit(auditId) {
  const response = await fetch(`${API_BASE_URL}/audits/${auditId}/rerun`, {
    method: 'POST',
    headers: getHeaders(),
    credentials: 'include',
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to rerun audit');
  }
  return data;
}

export async function downloadAuditPdf(auditId, filename = null) {
  const response = await fetch(`${API_BASE_URL}/audits/${auditId}/export-pdf`, {
    method: 'GET',
    headers: getHeaders(),
    credentials: 'include',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to generate PDF report');
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename || `devlens-audit-${auditId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(downloadUrl);
}

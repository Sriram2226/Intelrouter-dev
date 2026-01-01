// API Client Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Get auth token from localStorage (set by auth context)
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Get admin secret from localStorage or env
const getAdminSecret = (): string | null => {
  return localStorage.getItem('admin_secret') || import.meta.env.VITE_ADMIN_SECRET || null;
};

// Base fetch wrapper with auth headers
const apiFetch = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  // Add admin secret if provided
  const adminSecret = getAdminSecret();
  if (adminSecret && endpoint.includes('/admin/')) {
    headers['X-Admin-Secret'] = adminSecret;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response;
};

// API Methods
export const api = {
  // Query
  submitQuery: async (query: string, difficultyOverride?: string | null) => {
    const response = await apiFetch('/api/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        difficulty_override: difficultyOverride || null,
      }),
    });
    return response.json();
  },

  // Dashboard
  getMe: async () => {
    const response = await apiFetch('/api/me');
    return response.json();
  },

  getUsageToday: async () => {
    const response = await apiFetch('/api/usage/today');
    return response.json();
  },

  getQueryHistory: async () => {
    const response = await apiFetch('/api/queries/history');
    return response.json();
  },

  getOverrideStatus: async () => {
    const response = await apiFetch('/api/overrides/remaining');
    return response.json();
  },

  // Admin
  getAdminMetrics: async () => {
    const response = await apiFetch('/api/admin/metrics');
    return response.json();
  },

  getAdminCosts: async () => {
    const response = await apiFetch('/api/admin/costs');
    return response.json();
  },

  getAdminRoutingStats: async () => {
    const response = await apiFetch('/api/admin/routing-stats');
    return response.json();
  },
};

export default api;


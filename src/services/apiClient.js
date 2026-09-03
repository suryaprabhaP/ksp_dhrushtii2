/**
 * Centralized API Client (SOLID - DIP)
 * Provides environment-driven endpoint URL resolution and request wrappers.
 * Automatically adapts between localhost and Catalyst Serverless AppSail cloud.
 */

export const API_BASE_URL = (() => {
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://127.0.0.1:5000';
    }
    // Catalyst Serverless AppSail cloud domain resolution
    if (host.includes('catalystserverless.in') || host.includes('catalystappsail.in')) {
      const parts = host.split('.');
      const env = parts[1] || 'development';
      const hostPrefix = parts[0] || '';
      const orgMatch = hostPrefix.match(/\d{5,}/);
      const orgId = orgMatch ? orgMatch[0] : '60077159195';
      return `https://ksp-backend-${orgId}.${env}.catalystappsail.in`;
    }
  }
  return 'http://127.0.0.1:5000';
})().replace(/\/$/, '');

export function getApiUrl(endpoint) {
  if (!endpoint) return API_BASE_URL;
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) return endpoint;
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${cleanEndpoint}`;
}

export async function getJson(endpoint, options = {}) {
  const url = getApiUrl(endpoint);
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });
  return response;
}

export async function postJson(endpoint, body, options = {}) {
  const url = getApiUrl(endpoint);
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    body: JSON.stringify(body),
    ...options
  });
  return response;
}

/**
 * Fetches dynamic Zoho Analytics publish/embed URL with optional theme and view parameters
 */
export async function getAnalyticsDashboardUrl(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.view_id) searchParams.append('view_id', params.view_id);
  if (params.workspace_id) searchParams.append('workspace_id', params.workspace_id);
  if (params.theme) searchParams.append('theme', params.theme);

  const query = searchParams.toString();
  const endpoint = `/api/analytics/dashboard-url${query ? `?${query}` : ''}`;
  const response = await getJson(endpoint);
  if (!response.ok) {
    throw new Error(`Failed to fetch analytics dashboard URL (HTTP ${response.status})`);
  }
  return response.json();
}

/**
 * Fetches Section 65B forensic certification and compliance status
 */
export async function getAnalyticsEvidentiaryStatus() {
  const response = await getJson('/api/analytics/evidentiary-status');
  if (!response.ok) {
    throw new Error(`Failed to fetch evidentiary status (HTTP ${response.status})`);
  }
  return response.json();
}


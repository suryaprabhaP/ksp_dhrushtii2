/**
 * KSP DRISHTI — Portals API Client (SOLID: SRP)
 * Handles communication with the backend portal REST endpoints.
 */
import { getApiUrl } from './apiClient';

/**
 * Helper to fetch data with standardized error handling
 */
async function fetchWithConfig(endpoint, options = {}) {
  const url = getApiUrl(endpoint);
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP Error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`[Portal API] Error calling ${endpoint}:`, error);
    throw error;
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// E-Complaints API
// ══════════════════════════════════════════════════════════════════════════════
export const ComplaintAPI = {
  /**
   * Fetch complaints
   * @param {Object} filters { station, district, division, is_head }
   */
  getComplaints: async (filters = {}) => {
    const query = new URLSearchParams(filters).toString();
    const data = await fetchWithConfig(`/api/complaints?${query}`);
    return data.complaints || [];
  },

  /**
   * Submit a new E-Complaint
   * @param {Object} payload Complaint form data
   */
  submitComplaint: async (payload) => {
    return fetchWithConfig('/api/complaints', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
};

// ══════════════════════════════════════════════════════════════════════════════
// Passport Verification API
// ══════════════════════════════════════════════════════════════════════════════
export const PassportAPI = {
  /**
   * Fetch passport verification records
   */
  getPassports: async () => {
    const data = await fetchWithConfig('/api/passports');
    return data.records || [];
  },

  /**
   * Submit new passport verification request
   * @param {Object} payload Passport application data
   */
  submitPassport: async (payload) => {
    return fetchWithConfig('/api/passports', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Update passport verification status (Approve/Reject)
   * @param {string} rowId Zoho Catalyst ROWID
   * @param {string} status 'VERIFIED', 'REJECTED', 'FLAGGED'
   */
  updateStatus: async (rowId, status) => {
    return fetchWithConfig(`/api/passports/${rowId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, field_visit_completed: true }),
    });
  }
};

// ══════════════════════════════════════════════════════════════════════════════
// Police Initiated FIR API
// ══════════════════════════════════════════════════════════════════════════════
export const PoliceFirAPI = {
  /**
   * Fetch FIR records
   */
  getFirs: async () => {
    const data = await fetchWithConfig('/api/police_firs');
    return data.records || [];
  },

  /**
   * Submit a new Police-Initiated FIR
   * @param {Object} payload FIR form data
   */
  submitFir: async (payload) => {
    return fetchWithConfig('/api/police_firs', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
};

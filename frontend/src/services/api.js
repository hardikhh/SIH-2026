const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`API error (${response.status}): ${errText}`);
  }

  return response.json();
}

export const api = {
  // Voice API
  getWelcomePrompt: (lang = "hi") => fetchJson(`/voice/welcome?lang=${lang}`),
  sendVoiceTurn: (payload) =>
    fetchJson("/voice/turn", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Beneficiaries API
  listBeneficiaries: (district, status) => {
    const params = new URLSearchParams();
    if (district) params.append("district", district);
    if (status) params.append("status", status);
    return fetchJson(`/beneficiaries?${params.toString()}`);
  },
  getBeneficiary: (id) => fetchJson(`/beneficiaries/${id}`),

  // Recommendations API
  getRecommendations: (beneficiaryId) =>
    fetchJson(`/recommendations/beneficiary/${beneficiaryId}`),
  evaluateDirect: (profileData) =>
    fetchJson("/recommendations/evaluate-direct", {
      method: "POST",
      body: JSON.stringify(profileData),
    }),
  getCatalog: () => fetchJson("/recommendations/catalog"),

  // Admin API
  getAdminKPIs: () => fetchJson("/admin/kpis"),
  getDistricts: () => fetchJson("/admin/districts"),
  getInterventions: () => fetchJson("/admin/interventions"),
  createIntervention: (payload) =>
    fetchJson("/admin/interventions", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateIntervention: (id, payload) =>
    fetchJson(`/admin/interventions/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};

const DEFAULT_API_BASE_URL = import.meta.env.PROD ? "https://verticale-lead-finder.onrender.com" : "http://localhost:8000";
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, "");

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
  if (options.body && !isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers,
    ...options,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Erro ao comunicar com o servidor.");
  }

  return response;
}

function paramsFrom(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") params.set(key, value);
  });
  return params.toString();
}

export async function getDashboard() {
  const response = await request("/api/dashboard");
  return response.json();
}

export async function consultarCnpj(payload) {
  const response = await request("/api/cnpj/consultar", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return response.json();
}

export async function saveLead(payload) {
  const response = await request("/api/leads", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return response.json();
}

export async function getLeads(filters = {}) {
  const response = await request(`/api/leads?${paramsFrom(filters)}`);
  return response.json();
}

export async function getLead(id) {
  const response = await request(`/api/leads/${id}`);
  return response.json();
}

export async function updateLead(id, payload) {
  const response = await request(`/api/leads/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return response.json();
}

export async function deleteLead(id) {
  await request(`/api/leads/${id}`, { method: "DELETE" });
}

export async function exportLeads(format, payload) {
  const response = await request(`/api/exportar/${format}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  const blob = await response.blob();
  const disposition = response.headers.get("content-disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  return { blob, filename: match?.[1] || `leads.${format}` };
}

export async function importCsv(file) {
  const body = new FormData();
  body.append("file", file);

  const response = await request("/api/importar/csv", {
    method: "POST",
    body,
  });
  return response.json();
}

export async function importPdf(file) {
  const body = new FormData();
  body.append("file", file);

  const response = await request("/api/importar/pdf", {
    method: "POST",
    body,
  });
  return response.json();
}

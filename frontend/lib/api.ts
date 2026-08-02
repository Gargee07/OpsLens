const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function runQuery(symptomDescription: string) {
  const res = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symptom_description: symptomDescription }),
  });
  return res.json();
}

export async function resolveIncident(
  query: string,
  resolutionNotes: string,
  service = "unknown",
  severity = "SEV3"
) {
  const res = await fetch(`${API_URL}/api/incidents/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, resolution_notes: resolutionNotes, service, severity }),
  });
  return res.json();
}

export async function listIncidents() {
  const res = await fetch(`${API_URL}/api/incidents`, { cache: "no-store" });
  return res.json();
}

export async function getIncident(id: string) {
  const res = await fetch(`${API_URL}/api/incidents/${id}`, { cache: "no-store" });
  return res.json();
}

import Link from "next/link";
import { getIncident } from "@/lib/api";

export default async function IncidentDetailPage({ params }: { params: { id: string } }) {
  const incident = await getIncident(params.id);

  if (incident.error) {
    return <main className="max-w-3xl mx-auto px-6 py-12">Incident not found.</main>;
  }

  return (
    <main className="max-w-3xl mx-auto px-6 py-12">
      <Link href="/incidents" className="text-sm text-slate-500 hover:text-slate-900">← Incident log</Link>

      <div className="mt-6 mb-6">
        <div className="flex gap-2 items-center mb-2">
          <span className="font-mono text-xs text-slate-400">{incident.incident_id}</span>
          <span className="text-xs bg-slate-100 rounded-full px-2 py-0.5">{incident.service}</span>
          <span className="text-xs bg-slate-100 rounded-full px-2 py-0.5">{incident.severity}</span>
          <span className="text-xs bg-slate-100 rounded-full px-2 py-0.5">{incident.root_cause}</span>
        </div>
        <h1 className="text-xl font-semibold text-slate-900">{incident.symptom_description}</h1>
      </div>

      <div className="border border-slate-200 rounded-xl p-6 mb-6">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Postmortem</span>
        <p className="text-slate-800 leading-relaxed whitespace-pre-line mt-2">{incident.doc_text}</p>
      </div>

      {incident.resolution_steps?.length > 0 && (
        <div className="border border-slate-200 rounded-xl p-6 mb-6">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Resolution steps</span>
          <ol className="list-decimal list-inside mt-2 space-y-1 text-slate-800">
            {incident.resolution_steps.map((s: string, idx: number) => <li key={idx}>{s}</li>)}
          </ol>
        </div>
      )}

      {incident.related_incidents?.length > 0 && (
        <div>
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Related incidents (same root cause)</span>
          <div className="flex gap-2 mt-2 flex-wrap">
            {incident.related_incidents.map((id: string) => (
              <Link key={id} href={`/incidents/${id}`} className="text-xs bg-slate-100 hover:bg-slate-200 rounded-full px-3 py-1 font-mono">
                {id}
              </Link>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}

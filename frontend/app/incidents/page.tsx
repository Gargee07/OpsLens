import Link from "next/link";
import { listIncidents } from "@/lib/api";

export default async function IncidentsPage() {
  const incidents = await listIncidents();

  return (
    <main className="max-w-3xl mx-auto px-6 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Incident log</h1>
        <Link href="/" className="text-sm text-slate-500 hover:text-slate-900">← Search</Link>
      </div>

      <div className="space-y-2">
        {incidents.map((i: any) => (
          <Link
            key={i.incident_id}
            href={`/incidents/${i.incident_id}`}
            className="block border border-slate-200 rounded-lg p-4 hover:border-slate-400 transition-colors"
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono text-xs text-slate-400">{i.incident_id}</span>
                <span className="text-xs bg-slate-100 rounded-full px-2 py-0.5 ml-2">{i.service}</span>
                <span className="text-xs bg-slate-100 rounded-full px-2 py-0.5 ml-1">{i.severity}</span>
              </div>
              <span className="text-xs text-slate-400">{i.root_cause}</span>
            </div>
            <p className="text-sm text-slate-700 mt-2">{i.symptom_description}</p>
          </Link>
        ))}
      </div>
    </main>
  );
}

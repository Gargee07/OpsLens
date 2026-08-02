"use client";

import { useState } from "react";
import Link from "next/link";
import { runQuery, resolveIncident } from "@/lib/api";

const EXAMPLE_QUERIES = [
  "checkout-service p99 latency spiking, seems to correlate with inventory-service",
  "auth-service login failures spiking right after deploy",
  "legitimate payment requests getting 429 errors",
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [resolveStatus, setResolveStatus] = useState<string | null>(null);

  async function handleSearch(q: string) {
    setLoading(true);
    setResult(null);
    setResolveStatus(null);
    const data = await runQuery(q);
    setResult(data);
    setLoading(false);
  }

  async function handleResolve() {
    if (!resolutionNotes.trim()) return;
    const res = await resolveIncident(query, resolutionNotes);
    setResolveStatus(res.message || "Submitted.");
    setResolutionNotes("");
  }

  const confidencePct = result?.confidence ? Math.round(result.confidence * 100) : null;
  const confidenceLabel =
    confidencePct === null ? null : confidencePct >= 75 ? "High" : confidencePct >= 65 ? "Medium" : "Low";
  const confidenceColor =
    confidenceLabel === "High" ? "bg-green-100 text-green-800" :
    confidenceLabel === "Medium" ? "bg-yellow-100 text-yellow-800" :
    "bg-red-100 text-red-800";

  return (
    <main className="max-w-3xl mx-auto px-6 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">OpsLens</h1>
        <Link href="/incidents" className="text-sm text-slate-500 hover:text-slate-900">
          Incident log →
        </Link>
      </div>

      <p className="text-slate-500 mb-4">Describe the symptom you're seeing</p>
      <div className="flex gap-2 mb-3">
        <input
          className="flex-1 border border-slate-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
          placeholder="e.g. checkout-service returning 500s since ~2pm, right after a deploy"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch(query)}
        />
        <button
          className="bg-slate-900 text-white rounded-lg px-5 py-3 text-sm font-medium disabled:opacity-50"
          onClick={() => handleSearch(query)}
          disabled={!query.trim() || loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <div className="flex flex-wrap gap-2 mb-10">
        {EXAMPLE_QUERIES.map((q) => (
          <button
            key={q}
            className="text-xs bg-slate-100 hover:bg-slate-200 rounded-full px-3 py-1.5 text-slate-600"
            onClick={() => { setQuery(q); handleSearch(q); }}
          >
            {q}
          </button>
        ))}
      </div>

      {result && (
        <div className="border border-slate-200 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Answer</span>
            {confidenceLabel && (
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${confidenceColor}`}>
                {confidenceLabel} confidence ({confidencePct}%)
              </span>
            )}
          </div>

          <p className="text-slate-800 leading-relaxed whitespace-pre-line mb-4">{result.answer}</p>

          {result.sources?.length > 0 && (
            <div className="mb-4">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Sources</span>
              <div className="flex gap-2 mt-2 flex-wrap">
                {result.sources.map((id: string) => (
                  <Link key={id} href={`/incidents/${id}`} className="text-xs bg-slate-100 hover:bg-slate-200 rounded-full px-3 py-1 font-mono">
                    {id}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {result.closest_partials?.length > 0 && (
            <div className="mb-4">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Closest partial matches</span>
              <div className="mt-2 space-y-2">
                {result.closest_partials.map((p: any) => (
                  <div key={p.incident_id} className="text-sm bg-slate-50 rounded-lg p-3">
                    <span className="font-mono text-xs text-slate-500">{p.incident_id}</span>
                    <span className="text-slate-400 text-xs ml-2">{p.root_cause}</span>
                    <p className="text-slate-600 mt-1">{p.snippet}...</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="border-t border-slate-100 pt-4 mt-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Mark as resolved</span>
            <div className="flex gap-2 mt-2">
              <input
                className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm"
                placeholder="What actually fixed it?"
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
              />
              <button
                className="bg-slate-100 hover:bg-slate-200 rounded-lg px-4 py-2 text-sm font-medium"
                onClick={handleResolve}
              >
                Submit
              </button>
            </div>
            {resolveStatus && <p className="text-xs text-green-700 mt-2">{resolveStatus}</p>}
          </div>
        </div>
      )}
    </main>
  );
}

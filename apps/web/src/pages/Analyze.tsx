import { useState, type FormEvent } from "react";
import { createAnalysis } from "../api/client";
import MatchView from "../components/report/MatchView";
import { SAMPLE_CV, SAMPLE_JD } from "../samples";
import type { Report } from "../types/report";

export default function Analyze() {
  const [cvText, setCvText] = useState("");
  const [jdText, setJdText] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await createAnalysis({ cv_text: cvText, jd_text: jdText });
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">New analysis</h2>
          <button
            type="button"
            onClick={() => {
              setCvText(SAMPLE_CV);
              setJdText(SAMPLE_JD);
            }}
            className="rounded border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100"
          >
            Load sample
          </button>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">CV</span>
          <textarea
            value={cvText}
            onChange={(e) => setCvText(e.target.value)}
            rows={12}
            placeholder="Paste or upload the CV text…"
            className="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-sm"
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Job description</span>
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            rows={12}
            placeholder="Paste the job description…"
            className="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-sm"
          />
        </label>

        <button
          type="submit"
          disabled={loading || !cvText.trim() || !jdText.trim()}
          className="rounded bg-indigo-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>

        {error && <p className="text-sm text-rose-600">{error}</p>}
      </form>

      <div>
        {report ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span>mode: {report.meta.mode}</span>
              <span>confidence: {report.meta.confidence}</span>
              <span>pipeline: {report.meta.pipeline_version}</span>
            </div>
            <MatchView match={report.match} />
          </div>
        ) : (
          <p className="text-sm text-slate-400">Results will appear here.</p>
        )}
      </div>
    </div>
  );
}

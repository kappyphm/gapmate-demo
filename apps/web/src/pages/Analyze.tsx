import { useState, type FormEvent } from "react";
import { createAnalysis } from "../api/client";
import AtsView from "../components/report/AtsView";
import MatchView from "../components/report/MatchView";
import SuggestionsView from "../components/report/SuggestionsView";
import { DEFAULT_SAMPLE, SAMPLE_GROUPS, SAMPLES } from "../samples";
import type { Report } from "../types/report";

type Tab = "match" | "ats" | "suggestions";

const TABS: { id: Tab; label: string }[] = [
  { id: "match", label: "Match" },
  { id: "ats", label: "ATS" },
  { id: "suggestions", label: "Suggestions" },
];

export default function Analyze() {
  const [cvText, setCvText] = useState("");
  const [jdText, setJdText] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [tab, setTab] = useState<Tab>("match");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sampleId, setSampleId] = useState(DEFAULT_SAMPLE.id);

  function onLoadSample() {
    const sample = SAMPLES.find((s) => s.id === sampleId) ?? DEFAULT_SAMPLE;
    setCvText(sample.cv);
    setJdText(sample.jd);
    setReport(null);
    setError(null);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await createAnalysis({ cv_text: cvText, jd_text: jdText });
      setReport(result);
      setTab("match");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold">New analysis</h2>
          <div className="mt-2 flex items-center gap-2">
            <select
              value={sampleId}
              onChange={(e) => setSampleId(e.target.value)}
              aria-label="Sample CV and job description"
              className="min-w-0 flex-1 rounded border border-slate-300 bg-white px-2 py-1 text-sm"
            >
              {SAMPLE_GROUPS.map((group) => (
                <optgroup key={group.industry} label={group.industry}>
                  {group.samples.map((sample) => (
                    <option key={sample.id} value={sample.id}>
                      {sample.label}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <button
              type="button"
              onClick={onLoadSample}
              className="shrink-0 rounded border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100"
            >
              Load sample
            </button>
          </div>
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
          <span className="text-sm font-medium text-slate-700">
            Job description
          </span>
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

            <div className="flex gap-1 border-b border-slate-200">
              {TABS.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTab(t.id)}
                  className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium ${
                    tab === t.id
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-slate-500 hover:text-slate-700"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {tab === "match" && <MatchView match={report.match} />}
            {tab === "ats" &&
              (report.ats ? (
                <AtsView ats={report.ats} />
              ) : (
                <p className="text-sm text-slate-500">No ATS data.</p>
              ))}
            {tab === "suggestions" && (
              <SuggestionsView
                suggestions={report.suggestions}
                preview={report.ats_preview}
              />
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-400">Results will appear here.</p>
        )}
      </div>
    </div>
  );
}

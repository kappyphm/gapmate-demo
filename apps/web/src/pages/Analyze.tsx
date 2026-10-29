import { useEffect, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { createAnalysis } from "../api/client";
import AtsView from "../components/report/AtsView";
import CoursesView from "../components/report/CoursesView";
import MatchView from "../components/report/MatchView";
import RoadmapView from "../components/report/RoadmapView";
import SuggestionsView from "../components/report/SuggestionsView";
import { DEFAULT_SAMPLE, SAMPLE_GROUPS, SAMPLES } from "../samples";
import type { Report } from "../types/report";

type Tab = "match" | "ats" | "suggestions" | "roadmap" | "courses";

const TABS: { id: Tab; label: string }[] = [
  { id: "match", label: "Match" },
  { id: "ats", label: "ATS" },
  { id: "suggestions", label: "Suggestions" },
  { id: "roadmap", label: "Roadmap" },
  { id: "courses", label: "Courses" },
];

const TEXTAREA_CLASS =
  "mt-1 w-full rounded-lg border border-slate-300 p-3 font-mono text-sm shadow-sm transition focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100";

export default function Analyze() {
  const [cvText, setCvText] = useState("");
  const [jdText, setJdText] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [tab, setTab] = useState<Tab>("match");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sampleId, setSampleId] = useState(DEFAULT_SAMPLE.id);
  const [searchParams] = useSearchParams();

  // Landing page links here with ?sample=<id> to open a ready-made example.
  const sampleParam = searchParams.get("sample");
  useEffect(() => {
    if (!sampleParam) return;
    const sample = SAMPLES.find((s) => s.id === sampleParam);
    if (!sample) return;
    setSampleId(sample.id);
    setCvText(sample.cv);
    setJdText(sample.jd);
    setReport(null);
    setError(null);
  }, [sampleParam]);

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
    setReport(null);
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
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">
        Analyze a CV against a job description
      </h1>
      <p className="mt-2 max-w-2xl text-slate-600">
        Paste both documents — or start from a built-in sample — and get a match
        score, an ATS audit, prioritized skill gaps, a roadmap and course
        recommendations.
      </p>

      <div className="mt-8 grid items-start gap-6 lg:grid-cols-2">
        <form
          onSubmit={onSubmit}
          className="space-y-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              New analysis
            </h2>
            <label className="mt-3 block text-sm font-medium text-slate-700">
              Start from a sample
            </label>
            <div className="mt-1.5 flex items-center gap-2">
              <select
                value={sampleId}
                onChange={(e) => setSampleId(e.target.value)}
                aria-label="Sample CV and job description"
                className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
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
                className="shrink-0 rounded-lg border border-slate-300 px-3.5 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
              >
                Load sample
              </button>
            </div>
          </div>

          <label className="block">
            <span className="flex items-baseline justify-between text-sm font-medium text-slate-700">
              CV
              <span className="text-xs font-normal text-slate-400">
                {cvText.length} characters
              </span>
            </span>
            <textarea
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              rows={12}
              placeholder="Paste or upload the CV text…"
              className={TEXTAREA_CLASS}
            />
          </label>

          <label className="block">
            <span className="flex items-baseline justify-between text-sm font-medium text-slate-700">
              Job description
              <span className="text-xs font-normal text-slate-400">
                {jdText.length} characters
              </span>
            </span>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              rows={12}
              placeholder="Paste the job description…"
              className={TEXTAREA_CLASS}
            />
          </label>

          <button
            type="submit"
            disabled={loading || !cvText.trim() || !jdText.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 font-medium text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading && (
              <span
                className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"
                aria-hidden="true"
              />
            )}
            {loading ? "Analyzing…" : "Analyze"}
          </button>

          {error && (
            <div
              role="alert"
              className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
            >
              {error}
            </div>
          )}
        </form>

        <div>
          {loading && !report && (
            <div
              className="animate-pulse space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
              aria-label="Analyzing"
            >
              <div className="h-5 w-1/3 rounded bg-slate-200" />
              <div className="flex items-center gap-6">
                <div className="h-28 w-28 shrink-0 rounded-full bg-slate-200" />
                <div className="flex-1 space-y-3">
                  <div className="h-3 rounded bg-slate-200" />
                  <div className="h-3 rounded bg-slate-200" />
                  <div className="h-3 w-2/3 rounded bg-slate-200" />
                </div>
              </div>
              <div className="h-3 rounded bg-slate-200" />
              <div className="h-3 w-5/6 rounded bg-slate-200" />
            </div>
          )}

          {report ? (
            <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span className="rounded-full bg-slate-100 px-2.5 py-1">
                  mode: {report.meta.mode}
                </span>
                <span className="rounded-full bg-slate-100 px-2.5 py-1">
                  confidence: {report.meta.confidence}
                </span>
                <span className="rounded-full bg-slate-100 px-2.5 py-1">
                  pipeline: {report.meta.pipeline_version}
                </span>
              </div>

              <div className="flex gap-1 overflow-x-auto border-b border-slate-200">
                {TABS.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTab(t.id)}
                    className={`-mb-px shrink-0 border-b-2 px-3 py-2 text-sm font-medium transition ${
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
              {tab === "roadmap" && (
                <RoadmapView gaps={report.gaps} roadmap={report.roadmap} />
              )}
              {tab === "courses" && <CoursesView courses={report.courses} />}
            </div>
          ) : (
            !loading && (
              <div className="rounded-2xl border-2 border-dashed border-slate-300 bg-white/60 p-8">
                <h2 className="font-semibold text-slate-800">
                  Your report will appear here
                </h2>
                <ol className="mt-4 space-y-3 text-sm text-slate-600">
                  <li>
                    <span className="font-semibold text-indigo-600">1.</span>{" "}
                    Load a sample or paste your own CV and job description.
                  </li>
                  <li>
                    <span className="font-semibold text-indigo-600">2.</span>{" "}
                    Press <span className="font-medium">Analyze</span>.
                  </li>
                  <li>
                    <span className="font-semibold text-indigo-600">3.</span>{" "}
                    Explore the five tabs: Match, ATS, Suggestions, Roadmap and
                    Courses.
                  </li>
                </ol>
                <p className="mt-5 rounded-lg bg-indigo-50 px-3.5 py-2.5 text-sm text-indigo-800">
                  Tip: the built-in samples cover {SAMPLE_GROUPS.length}{" "}
                  industries, in Vietnamese and English — the fastest way to see
                  a full report.
                </p>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

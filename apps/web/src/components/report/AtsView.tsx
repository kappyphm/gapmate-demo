import type { AtsIssue, AtsSection } from "../../types/report";

const SEVERITY_STYLE: Record<AtsIssue["severity"], string> = {
  critical: "border-rose-200 bg-rose-50 text-rose-700",
  warn: "border-amber-200 bg-amber-50 text-amber-700",
  info: "border-slate-200 bg-slate-50 text-slate-600",
};

const ORDER: Record<AtsIssue["severity"], number> = {
  critical: 0,
  warn: 1,
  info: 2,
};

function ScoreRing({
  score,
  projected,
}: {
  score: number;
  projected: number | null;
}) {
  const color =
    score >= 75
      ? "border-emerald-500"
      : score >= 50
        ? "border-amber-500"
        : "border-rose-500";
  return (
    <div className="flex items-center gap-4">
      <div
        className={`flex h-24 w-24 flex-col items-center justify-center rounded-full border-4 ${color}`}
      >
        <span className="text-2xl font-bold text-slate-800">{score}</span>
        <span className="text-xs text-slate-500">/ 100</span>
      </div>
      {projected !== null && projected > score && (
        <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
          {score} → {projected} after fixes
        </span>
      )}
    </div>
  );
}

export default function AtsView({ ats }: { ats: AtsSection }) {
  const failed = [...ats.issues]
    .filter((i) => !i.pass)
    .sort((a, b) => ORDER[a.severity] - ORDER[b.severity]);
  const passed = [...ats.issues].filter((i) => i.pass);
  const { matched, missing } = ats.keyword_coverage;

  return (
    <div className="space-y-6">
      <ScoreRing score={ats.score} projected={ats.projected_score} />

      <section>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">
          Issues to fix ({failed.length})
        </h3>
        {failed.length === 0 ? (
          <p className="text-sm text-emerald-700">
            No blockers found — this CV passes every check.
          </p>
        ) : (
          <ul className="space-y-2">
            {failed.map((issue) => (
              <li
                key={issue.code}
                className={`rounded border px-3 py-2 text-sm ${
                  SEVERITY_STYLE[issue.severity]
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold">
                    {issue.code}
                  </span>
                  <span className="rounded bg-white/60 px-1.5 py-0.5 text-xs uppercase tracking-wide">
                    {issue.severity}
                  </span>
                  <span>{issue.message}</span>
                </div>
                <p className="mt-1 text-xs opacity-90">Fix: {issue.fix}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <details className="rounded border border-slate-200 bg-slate-50 px-3 py-2">
        <summary className="cursor-pointer text-sm font-semibold text-slate-600">
          Passed checks ({passed.length}) — confirmations, not problems
        </summary>
        <ul className="mt-2 space-y-1">
          {passed.map((issue) => (
            <li key={issue.code} className="flex items-center gap-2 text-xs">
              <span className="font-mono font-semibold text-emerald-600">
                {issue.code}
              </span>
              <span className="text-slate-500">{issue.message}</span>
            </li>
          ))}
        </ul>
      </details>

      <section className="grid gap-4 md:grid-cols-2">
        <div>
          <h3 className="mb-2 text-sm font-semibold text-emerald-700">
            Keywords matched ({matched.length})
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {matched.map((kw) => (
              <span
                key={kw}
                className="rounded bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
        <div>
          <h3 className="mb-2 text-sm font-semibold text-rose-700">
            Keywords missing ({missing.length})
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {missing.map((kw) => (
              <span
                key={kw}
                className="rounded bg-rose-100 px-2 py-0.5 text-xs text-rose-700"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

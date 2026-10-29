import type { MatchResult } from "../../types/report";

const SUBSCORE_LABELS: Record<keyof MatchResult["subscores"], string> = {
  skills: "Skills",
  experience: "Experience",
  education: "Education",
  keywords: "Keywords",
};

function Bar({ value }: { value: number }) {
  const pct = Math.max(0, Math.min(100, value));
  const color =
    pct >= 75 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-500" : "bg-rose-500";
  return (
    <div className="h-2 w-full rounded bg-slate-200">
      <div
        className={`h-2 rounded transition-[width] duration-500 ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export default function MatchView({ match }: { match: MatchResult }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-6">
        <div className="flex h-28 w-28 flex-col items-center justify-center rounded-full border-4 border-indigo-500">
          <span className="text-3xl font-bold text-indigo-600">
            {match.overall}
          </span>
          <span className="text-xs text-slate-500">/ 100</span>
        </div>
        <div className="grid flex-1 grid-cols-2 gap-4">
          {(
            Object.keys(SUBSCORE_LABELS) as (keyof MatchResult["subscores"])[]
          ).map((key) => (
            <div key={key} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="font-medium text-slate-700">
                  {SUBSCORE_LABELS[key]}
                </span>
                <span className="text-slate-500">{match.subscores[key]}</span>
              </div>
              <Bar value={match.subscores[key]} />
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <section>
          <h3 className="mb-2 text-sm font-semibold text-emerald-700">
            Matched ({match.matched.length})
          </h3>
          <ul className="space-y-1">
            {match.matched.map((m) => (
              <li
                key={m.skill_id}
                className="flex items-center justify-between rounded border border-slate-200 px-3 py-1.5 text-sm"
              >
                <span className="font-mono text-slate-800">{m.skill_id}</span>
                <span className="text-xs text-slate-500">
                  {m.match_type} · {m.match_score}
                </span>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h3 className="mb-2 text-sm font-semibold text-rose-700">
            Missing ({match.missing.length})
          </h3>
          {match.missing.length === 0 ? (
            <p className="text-sm text-slate-500">
              No required skills missing.
            </p>
          ) : (
            <ul className="space-y-1">
              {match.missing.map((m) => (
                <li
                  key={m.skill_id}
                  className="flex items-center justify-between rounded border border-slate-200 px-3 py-1.5 text-sm"
                >
                  <span className="font-mono text-slate-800">{m.skill_id}</span>
                  {m.required && (
                    <span className="rounded bg-rose-100 px-2 py-0.5 text-xs text-rose-700">
                      required
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

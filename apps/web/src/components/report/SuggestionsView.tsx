import type { AtsPreview, SuggestionItem } from "../../types/report";

export default function SuggestionsView({
  suggestions,
  preview,
}: {
  suggestions: SuggestionItem[];
  preview: AtsPreview | null;
}) {
  if (suggestions.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No suggestions — this CV is already well optimized.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {preview && preview.after > preview.before && (
        <div className="rounded border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          Applying these suggestions projects the ATS score from{" "}
          <span className="font-semibold">{preview.before}</span> →{" "}
          <span className="font-semibold">{preview.after}</span>.
        </div>
      )}

      <ul className="space-y-3">
        {suggestions.map((s, i) => (
          <li
            key={`${s.code}-${i}`}
            className="rounded border border-slate-200 bg-white p-4"
          >
            <div className="mb-2 flex items-center gap-2 text-xs">
              <span className="font-mono font-semibold text-slate-600">
                {s.code}
              </span>
              <span className="rounded bg-slate-100 px-2 py-0.5 text-slate-600">
                {s.section}
              </span>
              {s.jd_keywords_addressed.map((kw) => (
                <span
                  key={kw}
                  className="rounded bg-indigo-100 px-2 py-0.5 text-indigo-700"
                >
                  {kw}
                </span>
              ))}
            </div>

            {s.original && (
              <p className="mb-1 text-sm text-slate-500 line-through decoration-rose-300">
                {s.original}
              </p>
            )}
            <p className="whitespace-pre-line text-sm font-medium text-slate-800">
              {s.improved}
            </p>
            <p className="mt-2 text-xs text-slate-500">{s.reason}</p>

            {s.needs_user_input.length > 0 && (
              <p className="mt-1 text-xs font-medium text-amber-600">
                Needs your input: {s.needs_user_input.join(", ")}
              </p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

import type { GapItem, RoadmapPhase } from "../../types/report";

const PRIORITY_STYLE: Record<GapItem["priority"], string> = {
  P0: "bg-rose-100 text-rose-700",
  P1: "bg-amber-100 text-amber-700",
  P2: "bg-emerald-100 text-emerald-700",
};

const PRIORITY_ORDER: GapItem["priority"][] = ["P0", "P1", "P2"];

function SkillChip({ skill }: { skill: string }) {
  return (
    <span className="rounded bg-indigo-100 px-2 py-0.5 font-mono text-xs text-indigo-700">
      {skill}
    </span>
  );
}

export default function RoadmapView({
  gaps,
  roadmap,
}: {
  gaps: GapItem[];
  roadmap: RoadmapPhase[];
}) {
  if (gaps.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No skill gaps — this CV covers the JD requirements.
      </p>
    );
  }

  const ordered = [...gaps].sort(
    (a, b) =>
      PRIORITY_ORDER.indexOf(a.priority) - PRIORITY_ORDER.indexOf(b.priority),
  );

  return (
    <div className="space-y-6">
      <section>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">
          Prioritized gaps ({gaps.length})
        </h3>
        <ul className="space-y-2">
          {ordered.map((g) => (
            <li
              key={g.skill_id}
              className="rounded border border-slate-200 px-3 py-2 text-sm"
            >
              <div className="flex flex-wrap items-center gap-2">
                <SkillChip skill={g.skill_id} />
                <span
                  className={`rounded px-2 py-0.5 text-xs font-semibold ${PRIORITY_STYLE[g.priority]}`}
                >
                  {g.priority}
                </span>
                {g.adjacent_to.length > 0 && (
                  <span className="text-xs text-emerald-600">
                    fast win — you already know {g.adjacent_to.join(", ")}
                  </span>
                )}
              </div>
              <p className="mt-1 text-xs text-slate-500">{g.reason}</p>
            </li>
          ))}
        </ul>
      </section>

      {roadmap.length > 0 && (
        <section>
          <h3 className="mb-2 text-sm font-semibold text-slate-700">
            90-day plan
          </h3>
          <ol className="space-y-3">
            {roadmap.map((phase) => (
              <li
                key={phase.phase}
                className="rounded border border-slate-200 bg-white p-4"
              >
                <div className="mb-2 flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-indigo-700">
                    {phase.phase}
                  </h4>
                  <span className="text-xs text-slate-500">
                    {phase.duration}
                  </span>
                </div>
                <div className="mb-2 flex flex-wrap gap-1.5">
                  {phase.focus_skills.map((skill) => (
                    <SkillChip key={skill} skill={skill} />
                  ))}
                </div>
                <ul className="list-inside list-disc space-y-0.5 text-sm text-slate-600">
                  {phase.milestones.map((milestone) => (
                    <li key={milestone}>{milestone}</li>
                  ))}
                </ul>
                {phase.resources.length > 0 && (
                  <p className="mt-2 text-xs text-slate-500">
                    Courses: {phase.resources.join(", ")}
                  </p>
                )}
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}

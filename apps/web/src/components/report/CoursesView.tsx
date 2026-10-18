import type { CourseRec } from "../../types/report";

export default function CoursesView({ courses }: { courses: CourseRec[] }) {
  if (courses.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No courses match the current gaps.
      </p>
    );
  }

  return (
    <ul className="space-y-3">
      {courses.map((course) => (
        <li
          key={course.course_id}
          className="rounded border border-slate-200 bg-white p-4"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">
                {course.url ? (
                  <a
                    href={course.url}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-indigo-600 hover:underline"
                  >
                    {course.title}
                  </a>
                ) : (
                  course.title
                )}
              </h3>
              <p className="text-xs text-slate-500">
                {course.provider} · {course.duration}
              </p>
            </div>
            <span className="shrink-0 rounded bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-500">
              {course.course_id}
            </span>
          </div>

          <div className="mt-2 flex flex-wrap gap-1.5">
            {course.skills_covered.map((skill) => (
              <span
                key={skill}
                className="rounded bg-indigo-100 px-2 py-0.5 font-mono text-xs text-indigo-700"
              >
                {skill}
              </span>
            ))}
          </div>

          <p className="mt-2 text-xs text-slate-500">{course.match_reason}</p>
        </li>
      ))}
    </ul>
  );
}

# 03 — Data Contracts

All cross-service payloads are validated by Pydantic (services) and mirrored by Zod (web).
Web TypeScript types are generated from the core_api OpenAPI schema.

## 1. `CVDoc` (parse_cv output)

```jsonc
{
  "language": "vi | en",
  "contact": { "name": "", "email": "", "phone": "", "linkedin": "", "github": "", "location": "" },
  "summary": "",
  "skills": [
    { "raw": "JS", "skill_id": "javascript", "level": 3, "evidence_span": "..." }
  ],
  "experience": [
    { "company": "", "title": "", "start": "YYYY-MM", "end": "YYYY-MM|present",
      "location": "", "seniority": "intern|junior|mid|senior|lead",
      "bullets": ["..."], "skills": ["react", "javascript"] }
  ],
  "education": [
    { "institution": "", "degree": "", "field": "", "start": "", "end": "", "gpa": "" }
  ],
  "certifications": [], "projects": [], "languages": [],
  "meta": { "pages": 1, "parse_confidence": 0.0 }
}
```

## 2. `JDDoc` (parse_jd output)

```jsonc
{
  "language": "vi | en",
  "title": "", "seniority": "junior|mid|senior", "location": "",
  "employment_type": "full-time|part-time|contract|intern",
  "requirements": [
    { "raw": "Thành thạo TypeScript", "skill_id": "typescript", "type": "hard|soft",
      "importance": 0.0, "required": true, "level": 3, "category": "programming_language" }
  ],
  "responsibilities": [], "nice_to_have": [], "keywords": []
}
```

## 3. `Report` (full analysis output)

```jsonc
{
  "meta": { "pipeline_version": "0.1.0", "created_at": "ISO8601", "confidence": 0.0 },
  "match": {
    "overall": 0, "subscores": { "skills": 0, "experience": 0, "education": 0, "keywords": 0 },
    "matched":  [ { "skill_id": "", "match_score": 1.0, "match_type": "exact|alias|semantic|llm", "evidence_span": "" } ],
    "missing":  [ { "skill_id": "", "required": true, "importance": 1.0 } ],
    "evidence": []
  },
  "ats": {
    "score": 0,
    "issues": [ { "code": "A3", "severity": "critical|warn|info", "message": "", "fix": "" } ],
    "keyword_coverage": { "matched": [], "missing": [] },
    "format_issues": []
  },
  "gaps": [
    { "skill_id": "", "importance": 0.0, "current_level": 0, "target_level": 0,
      "priority": "P0|P1|P2", "reason": "", "adjacent_to": ["typescript"] }
  ],
  "roadmap": [
    { "phase": "0-30 days", "duration": "4 weeks", "focus_skills": ["typescript"],
      "milestones": [], "resources": ["c001"] }
  ],
  "courses": [
    { "course_id": "c001", "title": "", "provider": "", "skills_covered": [],
      "match_reason": "", "url": "", "duration": "" }
  ],
  "suggestions": [
    { "section": "experience[0].bullets[1]", "original": "", "improved": "",
      "reason": "", "jd_keywords_addressed": [], "needs_user_input": ["metric"] }
  ]
}
```

## 4. Skill taxonomy entry

```jsonc
{
  "skill_id": "javascript",
  "canonical_name": "JavaScript",
  "type": "hard|soft|tool|language|domain|methodology|certification",
  "category": "",
  "parents": [],
  "aliases": { "vi": [], "en": [] },
  "related": [],
  "esco_uri": "",  // optional reference
  "onet_code": ""  // optional reference
}
```

File: `data/skills-taxonomy.json`. Embeddings are precomputed at runtime and cached
(`data/.cache/`), NOT stored in the JSON.

## 5. Course catalog entry

```jsonc
{
  "course_id": "c001", "title": "", "provider": "", "url": "",
  "level": "beginner|intermediate|advanced", "duration_hours": 0, "price": 0,
  "language": "en|vi", "skills_covered": ["typescript", "react"],
  "description": "", "rating": 4.8
}
```

File: `data/courses.json`.

## 6. Contract generation

```bash
# 1. run core_api, 2. generate TS types
pnpm --filter @gapmate/shared-types generate
```

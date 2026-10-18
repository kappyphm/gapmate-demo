export interface MatchSubscores {
  skills: number;
  experience: number;
  education: number;
  keywords: number;
}

export interface MatchedItem {
  skill_id: string;
  match_score: number;
  match_type: string;
  evidence_span: string;
}

export interface MissingItem {
  skill_id: string;
  required: boolean;
  importance: number;
}

export interface MatchResult {
  overall: number;
  subscores: MatchSubscores;
  matched: MatchedItem[];
  missing: MissingItem[];
  evidence: string[];
}

export interface ReportMeta {
  pipeline_version: string;
  created_at: string;
  confidence: number;
  mode: string;
  role_template: string;
}

export interface AtsIssue {
  code: string;
  severity: "critical" | "warn" | "info";
  weight: number;
  pass: boolean;
  message: string;
  fix: string;
}

export interface KeywordCoverage {
  matched: string[];
  missing: string[];
}

export interface AtsSection {
  score: number;
  issues: AtsIssue[];
  keyword_coverage: KeywordCoverage;
  format_issues: string[];
  projected_score: number | null;
}

export interface SuggestionItem {
  section: string;
  original: string;
  improved: string;
  reason: string;
  jd_keywords_addressed: string[];
  needs_user_input: string[];
  code: string;
}

export interface AtsPreview {
  before: number;
  after: number;
}

export interface Report {
  meta: ReportMeta;
  match: MatchResult;
  ats: AtsSection | null;
  gaps: unknown[];
  roadmap: unknown[];
  courses: unknown[];
  suggestions: SuggestionItem[];
  ats_preview: AtsPreview | null;
}

export interface AnalyzeRequest {
  cv_text: string;
  jd_text: string;
  cv_layout?: Record<string, unknown>;
  options?: { role_template?: string; hours_per_week?: number };
}

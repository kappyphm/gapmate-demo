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

export interface Report {
  meta: ReportMeta;
  match: MatchResult;
  ats: Record<string, unknown> | null;
  gaps: unknown[];
  roadmap: unknown[];
  courses: unknown[];
  suggestions: unknown[];
}

export interface AnalyzeRequest {
  cv_text: string;
  jd_text: string;
  options?: { role_template?: string; hours_per_week?: number };
}

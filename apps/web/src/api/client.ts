import type { AnalyzeRequest, ExtractResult, Report } from "../types/report";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function createAnalysis(body: AnalyzeRequest): Promise<Report> {
  const resp = await fetch(`${API_URL}/analyses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(`Analysis failed (${resp.status}): ${detail}`);
  }
  return (await resp.json()) as Report;
}

/** Upload a CV/JD file (PDF, DOCX, TXT, MD — max 5 MB) and extract its text. */
export async function extractFile(file: File): Promise<ExtractResult> {
  const form = new FormData();
  form.append("file", file);
  const resp = await fetch(`${API_URL}/analyses/extract`, {
    method: "POST",
    body: form,
  });
  if (!resp.ok) {
    let message = `Upload failed (${resp.status})`;
    try {
      const data = (await resp.json()) as { detail?: string };
      if (data.detail) message = data.detail;
    } catch {
      // keep the generic message
    }
    throw new Error(message);
  }
  return (await resp.json()) as ExtractResult;
}

import type { AnalyzeRequest, Report } from "../types/report";

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

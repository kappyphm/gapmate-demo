"""Per-analysis LLM usage tracking + request logging (issues #4/#6)."""

import logging
from types import SimpleNamespace

from app.llm import gemini, usage
from app.pipeline.analyze import run_analysis
from app.schemas.report import AnalyzeRequest

CV = """# Jane Doe

## Skills
- Languages: Python, JavaScript
- Frameworks: React, FastAPI

## Experience
### Acme — Frontend Developer (2023 – nay)
- Built React dashboards for 12 screens, reduced load time by 35%.
"""

JD = """# Frontend Engineer

## Requirements
- React, TypeScript
- Testing with Vitest
"""


def test_tracker_accumulates_llm_and_embeddings():
    tracker, token = usage.start_tracking()
    try:
        meta = SimpleNamespace(
            prompt_token_count=100, candidates_token_count=40, total_token_count=140
        )
        tracker.record_llm(meta)
        tracker.record_llm(None)  # call without metadata still counts as a call
        tracker.record_embedding("hello")
        tracker.record_embedding("world!")
        snap = tracker.snapshot()
    finally:
        usage.stop_tracking(token)
    assert snap["llm_calls"] == 2
    assert snap["prompt_tokens"] == 100
    assert snap["output_tokens"] == 40
    assert snap["total_tokens"] == 140
    assert snap["embedding_calls"] == 2
    assert snap["embedding_input_chars"] == 11


def test_gemini_run_records_usage_metadata():
    class FakeResponse:
        text = '{"ok": true}'
        usage_metadata = SimpleNamespace(
            prompt_token_count=10, candidates_token_count=5, total_token_count=15
        )

    class FakeModel:
        def generate_content(self, prompt, generation_config=None, request_options=None):
            return FakeResponse()

    tracker, token = usage.start_tracking()
    try:
        result = gemini._run(FakeModel(), "prompt", None, 0.1)
        snap = tracker.snapshot()
    finally:
        usage.stop_tracking(token)
    assert result == {"ok": True}
    assert snap["llm_calls"] == 1
    assert snap["total_tokens"] == 15


def test_run_analysis_attaches_usage_and_logs_request(caplog):
    req = AnalyzeRequest(cv_text=CV, jd_text=JD)
    with caplog.at_level(logging.INFO, logger="app.pipeline.analyze"):
        report = run_analysis(req)
    assert report.meta.usage is not None
    # No GEMINI_API_KEY in tests → heuristic mode, no LLM calls, zero tokens.
    assert report.meta.usage["llm_calls"] == 0
    assert report.meta.usage["total_tokens"] == 0
    lines = [r.message for r in caplog.records if "analysis_request" in r.message]
    assert len(lines) == 1
    assert "total_tokens=0" in lines[0]
    assert "duration_ms=" in lines[0]
    assert f"overall={report.match.overall}" in lines[0]

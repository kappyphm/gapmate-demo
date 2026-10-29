"""POST /analyses/extract proxy + analysis request logging (issue #6)."""

import logging

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services import analysis_client

client = TestClient(app)


@pytest.fixture
def captured_extract(monkeypatch):
    calls = {}

    async def fake_extract(filename, data, content_type=None):
        calls.update(filename=filename, data=data, content_type=content_type)
        return {"text": "Jane Doe — React Developer", "layout": {"file_type": "pdf", "pages": 1}}

    monkeypatch.setattr(analysis_client, "extract", fake_extract)
    return calls


def test_extract_forwards_file_and_returns_payload(captured_extract):
    resp = client.post(
        "/analyses/extract",
        files={"file": ("cv.pdf", b"%PDF-fake-bytes", "application/pdf")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["text"].startswith("Jane Doe")
    assert body["layout"]["file_type"] == "pdf"
    assert captured_extract["filename"] == "cv.pdf"
    assert captured_extract["data"] == b"%PDF-fake-bytes"


def test_extract_rejection_from_analysis_api_is_400(monkeypatch):
    async def rejecting_extract(filename, data, content_type=None):
        raise HTTPException(status_code=400, detail="Unsupported file type: .rtf")

    monkeypatch.setattr(analysis_client, "extract", rejecting_extract)
    resp = client.post(
        "/analyses/extract",
        files={"file": ("cv.rtf", b"data", "application/rtf")},
    )
    assert resp.status_code == 400
    assert "Unsupported file type" in resp.json()["detail"]


def test_create_analysis_logs_request_and_usage(monkeypatch, caplog):
    async def fake_analyze(cv_text, jd_text, options, cv_layout=None):
        return {
            "meta": {
                "pipeline_version": "0.3.0",
                "mode": "gemini",
                "usage": {"total_tokens": 321, "llm_calls": 2},
            },
            "match": {"overall": 64},
        }

    monkeypatch.setattr(analysis_client, "analyze", fake_analyze)
    with caplog.at_level(logging.INFO, logger="app.api.routes.analyses"):
        resp = client.post("/analyses", json={"cv_text": "cv", "jd_text": "jd"})
    assert resp.status_code == 200
    messages = [r.message for r in caplog.records]
    assert any("analysis_request_received" in m for m in messages)
    assert any("analysis_request_completed" in m and "total_tokens=321" in m for m in messages)

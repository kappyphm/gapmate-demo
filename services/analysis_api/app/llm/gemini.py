"""Thin Gemini wrapper. Returns None when unavailable/failing so callers fall back."""

import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def available() -> bool:
    return bool(settings.gemini_api_key)


def generate_json(prompt: str, schema: dict | None = None, temperature: float = 0.1) -> dict | None:
    """Call Gemini, optionally with a JSON response schema. Returns parsed JSON or None."""
    if not available():
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        try:
            return _run(model, prompt, schema, temperature)
        except Exception as exc:  # noqa: BLE001 - e.g. schema "$defs" unsupported
            logger.warning("Gemini structured call failed (%s); retrying without schema", exc)
            return _run(model, prompt, None, temperature)
    except Exception as exc:  # noqa: BLE001 - fall back to heuristics on any failure
        logger.warning("Gemini call failed, falling back to heuristic: %s", exc)
        return None


def _run(model, prompt: str, schema: dict | None, temperature: float) -> dict | None:
    config: dict = {"response_mime_type": "application/json", "temperature": temperature}
    if schema is not None:
        config["response_schema"] = schema
    resp = model.generate_content(prompt, generation_config=config)
    return json.loads(resp.text)


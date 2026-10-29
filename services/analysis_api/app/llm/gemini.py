"""Thin Gemini wrapper. Returns None when unavailable/failing so callers fall back."""

import json
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# Transient errors worth retrying (overload, quota, network).
_TRANSIENT_MARKERS = ("503", "500", "429", "overloaded", "unavailable", "timeout", "deadline", "connection")
_MAX_TRANSIENT_RETRIES = 2
_RETRY_BASE_DELAY_SECONDS = 2.0


def available() -> bool:
    return bool(settings.gemini_api_key)


def _is_transient(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(marker in msg for marker in _TRANSIENT_MARKERS)


def generate_json(prompt: str, schema: dict | None = None, temperature: float = 0.1) -> dict | None:
    """Call Gemini, optionally with a JSON response schema. Returns parsed JSON or None."""
    if not available():
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        clean = _to_gemini_schema(schema) if schema else None
        try:
            return _call_with_transient_retry(model, prompt, clean, temperature)
        except Exception as exc:  # noqa: BLE001 - e.g. schema unsupported (non-transient)
            if _is_transient(exc):
                raise  # already retried; let outer handler fall back
            logger.warning("Gemini structured call failed (%s); retrying without schema", exc)
            return _call_with_transient_retry(model, prompt, None, temperature)
    except Exception as exc:  # noqa: BLE001 - fall back to heuristics on any failure
        logger.warning("Gemini call failed, falling back to heuristic: %s", exc)
        return None


def _call_with_transient_retry(model, prompt: str, schema: dict | None, temperature: float) -> dict | None:
    """Retry transient failures (503/429/timeout) up to _MAX_TRANSIENT_RETRIES times with backoff."""
    last_exc: Exception | None = None
    for attempt in range(_MAX_TRANSIENT_RETRIES + 1):
        try:
            return _run(model, prompt, schema, temperature)
        except Exception as exc:  # noqa: BLE001
            if not _is_transient(exc) or attempt >= _MAX_TRANSIENT_RETRIES:
                raise
            delay = _RETRY_BASE_DELAY_SECONDS * (2**attempt)
            logger.warning("Gemini transient error (attempt %d/%d), retrying in %.1fs: %s", attempt + 1, _MAX_TRANSIENT_RETRIES + 1, delay, exc)
            last_exc = exc
            time.sleep(delay)
    raise last_exc  # pragma: no cover - unreachable; loop always returns or raises


def _run(model, prompt: str, schema: dict | None, temperature: float) -> dict | None:
    config: dict = {"response_mime_type": "application/json", "temperature": temperature}
    if schema is not None:
        config["response_schema"] = schema
    # Bounded request (docs/07 §5): explicit timeout, no retries.
    options = {"timeout": settings.gemini_timeout_seconds, "retry": None}
    resp = model.generate_content(prompt, generation_config=config, request_options=options)
    if not resp.text:
        return None
    return json.loads(resp.text)


# Gemini's Schema type accepts only a small subset of JSON Schema.
_ALLOWED_KEYS = {
    "type",
    "format",
    "description",
    "enum",
    "items",
    "properties",
    "required",
    "nullable",
    "minimum",
    "maximum",
    "minItems",
    "maxItems",
    "minLength",
    "maxLength",
    "pattern",
}


def _to_gemini_schema(node, defs: dict | None = None) -> dict:
    """Convert a Pydantic JSON schema (with $defs/$ref/anyOf) into Gemini's Schema subset."""
    if defs is None:
        defs = node.get("$defs", {}) if isinstance(node, dict) else {}
    if isinstance(node, list):
        return [_to_gemini_schema(x, defs) for x in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        return _to_gemini_schema(defs.get(node["$ref"].split("/")[-1], {}), defs)
    if "anyOf" in node:
        options = node["anyOf"]
        non_null = [o for o in options if o.get("type") != "null"]
        has_null = any(o.get("type") == "null" for o in options)
        base = _to_gemini_schema(non_null[0], defs) if non_null else {"type": "string"}
        if has_null:
            base["nullable"] = True
        return base
    out: dict = {}
    for key, value in node.items():
        if key == "properties":
            out[key] = {pk: _to_gemini_schema(pv, defs) for pk, pv in value.items()}
        elif key == "items":
            out[key] = _to_gemini_schema(value, defs)
        elif key in _ALLOWED_KEYS:
            out[key] = value
    return out

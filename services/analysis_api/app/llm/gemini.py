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
        clean = _to_gemini_schema(schema) if schema else None
        try:
            return _run(model, prompt, clean, temperature)
        except Exception as exc:  # noqa: BLE001 - e.g. schema unsupported
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


# Gemini's Schema type accepts only a small subset of JSON Schema.
_ALLOWED_KEYS = {
    "type", "format", "description", "enum", "items", "properties", "required",
    "nullable", "minimum", "maximum", "minItems", "maxItems", "minLength", "maxLength", "pattern",
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



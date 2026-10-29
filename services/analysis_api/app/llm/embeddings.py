"""Gemini text embeddings with a small on-disk cache (data/.cache/).

Returns ``None`` whenever Gemini/embeddings are unavailable so callers degrade gracefully to
the deterministic cascade (docs/07 §5).
"""

import hashlib
import json
import logging
import math
from pathlib import Path

from app.core.config import settings
from app.llm import gemini, usage

logger = logging.getLogger(__name__)

_CACHE: dict[str, list[float]] = {}
_LOADED = False


def _cache_path() -> Path:
    return Path(settings.data_dir) / ".cache" / "embeddings.json"


def _load() -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    try:
        path = _cache_path()
        if path.exists():
            _CACHE.update(json.loads(path.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read embedding cache: %s", type(exc).__name__)


def _save() -> None:
    try:
        path = _cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_CACHE), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not write embedding cache: %s", type(exc).__name__)


def embed(text: str) -> list[float] | None:
    if not text or not text.strip() or not gemini.available():
        return None
    _load()
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
    vector = _call(text)
    if vector is None:
        return None
    _CACHE[key] = vector
    _save()
    return vector


def _call(text: str) -> list[float] | None:
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = settings.gemini_embed_model
        if not model.startswith(("models/", "tunedModels/")):
            model = f"models/{model}"
        resp = genai.embed_content(
            model=model,
            content=text,
            task_type="SEMANTIC_SIMILARITY",
            request_options={"timeout": settings.gemini_timeout_seconds, "retry": None},
        )
        usage.record_embedding(text)
        return list(resp["embedding"])
    except Exception as exc:  # noqa: BLE001 - degrade to deterministic cascade
        logger.warning("Embedding call failed (%s)", type(exc).__name__)
        return None


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)

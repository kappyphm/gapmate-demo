"""Per-analysis LLM usage tracking (issue #4, wired into #6).

A ``UsageTracker`` is installed in a context variable for the duration of one
analysis run. The Gemini wrapper and the embeddings helper record into it, and
the pipeline orchestrator reads the totals back to (a) attach them to the
report metadata and (b) emit one structured log line per analysis request.

Token counts come from the Gemini API's own ``usage_metadata`` on generation
responses. The embeddings API does not report token usage, so embedding calls
are tracked as call count + input characters instead of invented token numbers.
"""

import contextvars
from dataclasses import asdict, dataclass


@dataclass
class UsageTracker:
    llm_calls: int = 0
    prompt_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    embedding_calls: int = 0
    embedding_input_chars: int = 0

    def record_llm(self, usage_metadata: object | None) -> None:
        """Record one generation call; ``usage_metadata`` may be None."""
        self.llm_calls += 1
        if usage_metadata is None:
            return
        prompt = int(getattr(usage_metadata, "prompt_token_count", 0) or 0)
        output = int(getattr(usage_metadata, "candidates_token_count", 0) or 0)
        total = int(getattr(usage_metadata, "total_token_count", 0) or 0)
        self.prompt_tokens += prompt
        self.output_tokens += output
        self.total_tokens += total if total else prompt + output

    def record_embedding(self, text: str) -> None:
        self.embedding_calls += 1
        self.embedding_input_chars += len(text)

    def snapshot(self) -> dict:
        return asdict(self)


_current: contextvars.ContextVar[UsageTracker | None] = contextvars.ContextVar(
    "llm_usage_tracker", default=None
)


def start_tracking() -> tuple[UsageTracker, contextvars.Token]:
    """Install a fresh tracker for the current context; returns (tracker, token)."""
    tracker = UsageTracker()
    token = _current.set(tracker)
    return tracker, token


def stop_tracking(token: contextvars.Token) -> None:
    _current.reset(token)


def current() -> UsageTracker | None:
    return _current.get()


def record_llm(usage_metadata: object | None) -> None:
    tracker = _current.get()
    if tracker is not None:
        tracker.record_llm(usage_metadata)


def record_embedding(text: str) -> None:
    tracker = _current.get()
    if tracker is not None:
        tracker.record_embedding(text)

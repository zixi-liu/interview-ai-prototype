"""
Single LiteLLM entry point for paper_2_eval experiments.

All provider calls go through `acompletion` here so runs are auditable and mockable.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import litellm
from litellm import acompletion

litellm.drop_params = True

# Load repo-root .env when running scripts from paper_2_eval/
_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")


async def complete_text(
    model: str,
    prompt: str,
    *,
    max_tokens: int | None = 4096,
    timeout: float | None = 120.0,
    response_format_json: bool = False,
) -> str:
    """
    Non-streaming completion. Prefer JSON-capable models when response_format_json=True.
    """
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if timeout is not None:
        kwargs["timeout"] = timeout
    if response_format_json:
        # OpenAI-compatible; other providers may ignore or error — caller can disable.
        kwargs["response_format"] = {"type": "json_object"}

    response = await acompletion(**kwargs)
    if not response or not response.choices:
        return ""
    msg = response.choices[0].message
    content = getattr(msg, "content", None) if msg else None
    return (content or "").strip()


def provider_bucket_for_model(model: str) -> str:
    """
    Bucket name for rate limiting / concurrency (not necessarily LiteLLM provider id).
    """
    m = model.lower()
    if m.startswith("gemini/") or "/gemini" in m or m.startswith("vertex_ai/"):
        return "google"
    if "claude" in m or m.startswith("anthropic/"):
        return "anthropic"
    if "grok" in m or m.startswith("xai/"):
        return "xai"
    if m.startswith("gpt-") or m.startswith("o1") or m.startswith("o3") or m.startswith("o4"):
        return "openai"
    return "openai"

"""
Unified prompt schema and parser for BQ multi-model rating experiments.

This module defines:
- A single prompt template shared across all experiment stages.
- Canonical 5-level rating labels.
- Strict output format requirements.
- Fallback parsing rules when model output is malformed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


CANONICAL_RATINGS: tuple[str, ...] = (
    "No Hire",
    "Leaning No Hire",
    "Leaning Hire",
    "Hire",
    "Strong Hire",
)

RATING_ALIASES: dict[str, str] = {
    "no hire": "No Hire",
    "no-hire": "No Hire",
    "reject": "No Hire",
    "leaning no hire": "Leaning No Hire",
    "lean no hire": "Leaning No Hire",
    "lnh": "Leaning No Hire",
    "leaning hire": "Leaning Hire",
    "lean hire": "Leaning Hire",
    "lh": "Leaning Hire",
    "hire": "Hire",
    "pass": "Hire",
    "strong hire": "Strong Hire",
    "strong-hire": "Strong Hire",
    "sh": "Strong Hire",
}


STRICT_OUTPUT_SPEC = """
Output MUST be valid JSON with exactly these keys:
{
  "feedback": "<~200 words concise interviewer feedback>",
  "rating": "<one of: No Hire | Leaning No Hire | Leaning Hire | Hire | Strong Hire>"
}

Hard constraints:
- Do not output markdown.
- Do not output code fences.
- Do not output extra keys.
- "feedback" should be approximately 150-200 words.
- "rating" must match one of the 5 labels exactly.
""".strip()

EVALUATION_INSTRUCTIONS_TEMPLATE = """
Evaluation instructions:
- Judge by real-world bar for {company} behavioral interviews.
- Focus on ownership, problem solving, execution, collaboration, communication, leadership, and impact.
- Be strict and evidence-based. Do not give the benefit of the doubt when details are missing.
- Feedback should be concise, concrete, and decision-oriented.
""".strip()


@dataclass
class ParsedBQRating:
    """Normalized parsed output for experiment row writing."""

    feedback: str
    rating: str
    parse_error: bool
    error: str = ""
    raw_text: str = ""

    def to_row_payload(self) -> dict[str, Any]:
        return {
            "feedback": self.feedback,
            "rating": self.rating,
            "parse_error": self.parse_error,
            "error": self.error,
        }


def build_bq_rating_prompt(
    *,
    question: str,
    answer: str,
    company: str,
    level: str = "senior",
) -> str:
    """
    Build one unified evaluation prompt for all providers and stages.

    Keep this function stable across experiments for reproducibility.
    """
    eval_block = EVALUATION_INSTRUCTIONS_TEMPLATE.format(company=company)
    return f"""You are an interviewer at {company}.
Evaluate the candidate's behavioral answer for a {level} Software Engineer role.

Question:
{question}

Candidate answer:
{answer}

{STRICT_OUTPUT_SPEC}
"""


def parse_bq_rating_output(raw_text: str) -> ParsedBQRating:
    """
    Parse model output using strict JSON-first strategy with robust fallback.

    Fallback priority:
    1) JSON parse from full text.
    2) JSON parse from extracted fenced/braced block.
    3) Regex extract rating + cleaned remaining text as feedback.
    """
    text = (raw_text or "").strip()
    if not text:
        return ParsedBQRating(
            feedback="",
            rating="No Hire",
            parse_error=True,
            error="Empty model output",
            raw_text=raw_text,
        )

    # 1) Full text as JSON
    parsed = _try_parse_json_dict(text)
    if parsed is not None:
        normalized = _normalize_from_dict(parsed, raw_text)
        if not normalized.parse_error:
            return normalized

    # 2) Extract first JSON-like block
    json_block = _extract_json_block(text)
    if json_block:
        parsed = _try_parse_json_dict(json_block)
        if parsed is not None:
            normalized = _normalize_from_dict(parsed, raw_text)
            if not normalized.parse_error:
                return normalized

    # 3) Regex fallback
    rating = _extract_rating_fallback(text) or "No Hire"
    feedback = _clean_feedback(_extract_feedback_fallback(text))
    if not feedback:
        feedback = _clean_feedback(text)

    return ParsedBQRating(
        feedback=feedback,
        rating=rating,
        parse_error=True,
        error="Failed strict JSON parse; used regex fallback",
        raw_text=raw_text,
    )


def _try_parse_json_dict(text: str) -> dict[str, Any] | None:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(obj, dict):
        return obj
    return None


def _extract_json_block(text: str) -> str:
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()

    brace_match = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if brace_match:
        return brace_match.group(1).strip()

    return ""


def _normalize_from_dict(obj: dict[str, Any], raw_text: str) -> ParsedBQRating:
    rating_raw = str(obj.get("rating", "")).strip()
    feedback_raw = str(obj.get("feedback", "")).strip()

    rating = normalize_rating_label(rating_raw)
    feedback = _clean_feedback(feedback_raw)

    if not rating:
        return ParsedBQRating(
            feedback=feedback,
            rating="No Hire",
            parse_error=True,
            error="Invalid or missing rating in JSON",
            raw_text=raw_text,
        )
    if not feedback:
        return ParsedBQRating(
            feedback="",
            rating=rating,
            parse_error=True,
            error="Missing feedback in JSON",
            raw_text=raw_text,
        )

    return ParsedBQRating(
        feedback=feedback,
        rating=rating,
        parse_error=False,
        raw_text=raw_text,
    )


def normalize_rating_label(label: str) -> str:
    key = label.strip().lower()
    if not key:
        return ""
    if key in RATING_ALIASES:
        return RATING_ALIASES[key]
    return label.strip() if label.strip() in CANONICAL_RATINGS else ""


def _extract_rating_fallback(text: str) -> str:
    # Prefer exact canonical matches first to avoid "Hire" matching inside "Strong Hire".
    for canonical in sorted(CANONICAL_RATINGS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(canonical)}\b", text, flags=re.IGNORECASE):
            return canonical

    alias_keys = sorted(RATING_ALIASES.keys(), key=len, reverse=True)
    for alias in alias_keys:
        if re.search(rf"\b{re.escape(alias)}\b", text, flags=re.IGNORECASE):
            return RATING_ALIASES[alias]

    return ""


def _extract_feedback_fallback(text: str) -> str:
    # Remove likely rating lines and JSON key wrappers.
    cleaned = re.sub(
        r'("?\s*rating\s*"?\s*[:=]\s*"?[^"\n,}]+\"?)',
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r'["{}]', "", cleaned)
    cleaned = re.sub(r"\b(feedback)\b\s*[:=]", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _clean_feedback(text: str) -> str:
    normalized_ws = " ".join((text or "").replace("\r", " ").replace("\n", " ").split())
    if not normalized_ws:
        return ""

    # Keep roughly 200 words, but avoid over-truncating short responses.
    words = normalized_ws.split()
    if len(words) > 230:
        words = words[:230]
        if words[-1][-1].isalnum():
            words[-1] = words[-1] + "..."

    return " ".join(words)

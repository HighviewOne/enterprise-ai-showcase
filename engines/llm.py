"""Shared Anthropic helpers.

One place for the model name, the API call, truncation handling, and
robust JSON parsing — so every engine doesn't reimplement (and subtly
break) the same call/parse boilerplate.
"""

from __future__ import annotations

import json

import anthropic

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def call_claude(
    prompt: str,
    api_key: str,
    *,
    max_tokens: int = 4096,
    system: str | None = None,
    model: str = DEFAULT_MODEL,
) -> str:
    """Run a single-turn completion and return the response text.

    Raises ``TruncatedResponseError`` if the model hit ``max_tokens`` before
    finishing, which is the usual cause of "valid-looking but unparseable"
    output downstream.
    """
    client = anthropic.Anthropic(api_key=api_key)
    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system
    message = client.messages.create(**kwargs)
    return response_text(message)


def call_claude_json(
    prompt: str,
    api_key: str,
    *,
    max_tokens: int = 4096,
    system: str | None = None,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Run a completion and parse the response as JSON.

    Tolerates Markdown code fences and surrounding prose; raises
    ``ValueError`` if no valid JSON can be recovered.
    """
    return parse_json(
        call_claude(
            prompt, api_key, max_tokens=max_tokens, system=system, model=model
        )
    )


class TruncatedResponseError(RuntimeError):
    """Raised when the model stopped because it hit ``max_tokens``."""


def response_text(message) -> str:
    """Extract text from a messages API response, guarding against truncation."""
    if getattr(message, "stop_reason", None) == "max_tokens":
        raise TruncatedResponseError(
            "The response was cut off before completing (hit max_tokens). "
            "Reduce the size of the request or raise max_tokens."
        )
    return message.content[0].text.strip()


def parse_json(text: str) -> dict:
    """Parse JSON from a model response.

    Strips Markdown code fences, and if the text still won't parse, falls
    back to the outermost ``{...}`` / ``[...]`` span before giving up.
    """
    cleaned = _strip_code_fences(text.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        snippet = _outermost_json_span(cleaned)
        if snippet is not None:
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                pass
        raise ValueError(
            "The model did not return valid JSON. First 500 chars:\n"
            f"{text[:500]}"
        )


def parse_json_response(message) -> dict:
    """Convenience: ``parse_json(response_text(message))``."""
    return parse_json(response_text(message))


def _strip_code_fences(text: str) -> str:
    if text.startswith("```"):
        lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text


def _outermost_json_span(text: str) -> str | None:
    candidates = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not candidates:
        return None
    start = min(candidates)
    close = "}" if text[start] == "{" else "]"
    end = text.rfind(close)
    if end > start:
        return text[start : end + 1]
    return None

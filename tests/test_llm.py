"""Tests for engines.llm parsing/truncation helpers.

Runs standalone (``python tests/test_llm.py``) or under pytest.
"""

import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.llm import (  # noqa: E402
    TruncatedResponseError,
    parse_json,
    parse_json_response,
    response_text,
)


@dataclass
class _Block:
    text: str


@dataclass
class _FakeMessage:
    text: str
    stop_reason: str = "end_turn"

    @property
    def content(self):
        return [_Block(self.text)]


def test_parse_plain_json():
    assert parse_json('{"a": 1}') == {"a": 1}


def test_parse_fenced_json():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_json_with_surrounding_prose():
    text = 'Sure! Here is the result:\n{"a": 1, "b": [2, 3]}\nHope that helps.'
    assert parse_json(text) == {"a": 1, "b": [2, 3]}


def test_parse_json_array():
    assert parse_json("[1, 2, 3]") == [1, 2, 3]


def test_parse_invalid_json_raises():
    try:
        parse_json("not json at all")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_parse_json_response_integration():
    msg = _FakeMessage('```\n{"x": 1}\n```')
    assert parse_json_response(msg) == {"x": 1}


def test_truncation_raises():
    msg = _FakeMessage('{"partial":', stop_reason="max_tokens")
    try:
        response_text(msg)
    except TruncatedResponseError:
        pass
    else:
        raise AssertionError("expected TruncatedResponseError on max_tokens")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)} tests passed")

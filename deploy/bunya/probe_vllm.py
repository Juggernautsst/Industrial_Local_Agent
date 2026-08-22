#!/usr/bin/env python3
"""Run a local-only, synthetic smoke test against a vLLM OpenAI-compatible API."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import NoReturn


def fail(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def local_base_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        fail("base URL must be an HTTP loopback URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        fail("base URL must not contain credentials, query, or fragment")
    return value.rstrip("/")


def request_json(url: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        fail(f"request failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="qwen3.8-27b-fp8")
    args = parser.parse_args()
    base_url = local_base_url(args.base_url)

    models = request_json(f"{base_url}/v1/models")
    model_ids = {item.get("id") for item in models.get("data", []) if isinstance(item, dict)}
    if args.model not in model_ids:
        fail(f"served model {args.model!r} was not listed by /v1/models")

    payload = {
        "model": args.model,
        "messages": [
            {
                "role": "system",
                "content": "Return a concise answer for a synthetic deployment smoke test.",
            },
            {
                "role": "user",
                "content": "In one sentence, state that 2 + 2 = 4. Do not mention private data.",
            },
        ],
        "temperature": 0,
        "max_tokens": 128,
        "chat_template_kwargs": {"enable_thinking": False},
        "stream": False,
    }
    started = time.monotonic()
    result = request_json(f"{base_url}/v1/chat/completions", payload)
    elapsed_ms = round((time.monotonic() - started) * 1000, 1)
    choices = result.get("choices")
    if not isinstance(choices, list) or not choices:
        fail("chat completion returned no choices")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        fail("chat completion returned empty content")

    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    summary = {
        "status": "pass",
        "model": args.model,
        "elapsed_ms": elapsed_ms,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "content_chars": len(content),
        "content_sha256_prefix": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

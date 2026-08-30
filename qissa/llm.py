from __future__ import annotations

import json
import os
from typing import Any

# Official Google Cloud AI runtime import (accepted SDK: google-genai).
try:
    from google import genai
except Exception:
    genai = None  # type: ignore[misc, assignment]


def model_name() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


_CLIENT = None


def client():
    global _CLIENT
    if genai is None:
        raise RuntimeError("google-genai is not installed")
    if _CLIENT is not None:
        return _CLIENT

    if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true":
        _CLIENT = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    else:
        key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
        if not key:
            raise RuntimeError("GEMINI_API_KEY missing")
        _CLIENT = genai.Client(api_key=key)
    return _CLIENT


def generate_json(prompt: str) -> dict[str, Any]:
    response = client().models.generate_content(model=model_name(), contents=prompt)
    text = (getattr(response, "text", None) or "").strip()
    return extract_json(text)


def generate_text(prompt: str) -> str:
    response = client().models.generate_content(model=model_name(), contents=prompt)
    return (getattr(response, "text", None) or "").strip()


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[: cleaned.rfind("```")]
        cleaned = cleaned.strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(cleaned[start : end + 1])
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
    return {}

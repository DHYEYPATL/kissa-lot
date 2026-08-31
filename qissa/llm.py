from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger("qissa.llm")

# Official Google Cloud AI runtime import (accepted SDK: google-genai).
try:
    from google import genai
except Exception:
    genai = None  # type: ignore[misc, assignment]


def model_name() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


_CLIENT = None


def is_live_gemini() -> bool:
    """Check if Gemini API keys or Vertex AI are configured and available."""
    if genai is None:
        return False
    return bool(
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or (os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true" and os.environ.get("GOOGLE_CLOUD_PROJECT"))
    )


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
            raise RuntimeError("GEMINI_API_KEY is not set in environment or .env")
        _CLIENT = genai.Client(api_key=key)
    return _CLIENT


def generate_json(prompt: str, retries: int = 2) -> dict[str, Any]:
    """Generate structured JSON using Gemini with multiple extraction and retry fallbacks."""
    c = client()
    last_err = None
    for attempt in range(retries):
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7 if attempt == 0 else 0.4,
            )
            response = c.models.generate_content(model=model_name(), contents=prompt, config=config)
            text = (getattr(response, "text", None) or "").strip()
            parsed = extract_json(text)
            if parsed and isinstance(parsed, dict):
                return parsed
        except Exception as exc:
            last_err = exc
            logger.warning("generate_json attempt %d failed: %s", attempt + 1, exc)

    if last_err:
        raise last_err
    return {}


def generate_text(prompt: str) -> str:
    """Generate plain text from Gemini."""
    response = client().models.generate_content(model=model_name(), contents=prompt)
    return (getattr(response, "text", None) or "").strip()


def extract_json(text: str) -> dict[str, Any]:
    """Robustly extract and parse JSON object from model output."""
    if not text:
        return {}

    cleaned = text.strip()

    # Strip markdown code blocks
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Pass 1: Direct JSON parsing
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Pass 2: Extract outer JSON braces
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        snippet = cleaned[start : end + 1]
        try:
            parsed = json.loads(snippet)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            # Pass 3: Clean trailing commas or common syntax issues
            try:
                fixed = re.sub(r",\s*([\]}])", r"\1", snippet)
                parsed = json.loads(fixed)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    return {}

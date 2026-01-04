from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple

from openai import OpenAI


class LLMError(RuntimeError):
    pass


def _get_provider() -> str:
    return (os.getenv("LLM_PROVIDER") or "openai").strip().lower()


def chat_json(system: str, user: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Returns: (output_json_dict, meta)
    Works with:
      - OpenAI (requires OPENAI_API_KEY)
      - Hugging Face Router (requires HF_TOKEN)
    """
    provider = _get_provider()

    if provider == "huggingface":
        token = os.getenv("HF_TOKEN")
        model = os.getenv("HF_MODEL", "moonshotai/Kimi-K2-Instruct-0905")
        if not token:
            raise LLMError("HF_TOKEN is not set.")

        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=token,
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content or ""
        return _coerce_json(content), {"provider": "huggingface", "model": model}

    # default: OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise LLMError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    return _coerce_json(content), {"provider": "openai", "model": model}


def _coerce_json(text: str) -> Dict[str, Any]:
    """
    HF models sometimes return JSON in a code block or with extra text.
    This tries hard to extract JSON safely.
    """
    text = text.strip()

    # Strip ```json fences if present
    if text.startswith("```"):
        text = text.strip("`")
        # possible "json\n{...}"
        lines = text.splitlines()
        if len(lines) > 1 and lines[0].strip().lower() in ("json", "javascript"):
            text = "\n".join(lines[1:]).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try extracting the first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # Fallback
    return {"headline": "LLM output parsing failed", "raw": text}

import time
from openai import OpenAI
from .config import settings

client = OpenAI(api_key=settings.openai_api_key)

class OpenAIError(RuntimeError):
    pass

def chat_json(system: str, user: str) -> tuple[dict, dict]:
    """Returns (json_obj, meta)."""
    if not settings.openai_api_key:
        raise OpenAIError("OPENAI_API_KEY is not set.")
    t0 = time.time()
    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    dt = int((time.time() - t0) * 1000)
    msg = resp.choices[0].message.content
    import json
    try:
        obj = json.loads(msg)
    except Exception as e:
        raise OpenAIError(f"Model did not return valid JSON: {e}. Raw: {msg[:500]}")
    meta = {
        "model": resp.model,
        "latency_ms": dt,
        "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
        "completion_tokens": getattr(resp.usage, "completion_tokens", None),
        "total_tokens": getattr(resp.usage, "total_tokens", None),
    }
    return obj, meta

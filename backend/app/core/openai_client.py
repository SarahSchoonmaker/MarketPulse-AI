import os
from openai import OpenAI

# Hugging Face token (fine-grained, inference only)
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not set in environment")

# OpenAI-compatible client pointed at Hugging Face router
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

class LLMError(Exception):
    pass


def chat_json(
    system_prompt: str,
    user_prompt: str,
    model: str = "moonshotai/Kimi-K2-Instruct-0905",
):
    """
    Returns:
        (json_text: str, meta: dict)
    """
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
    except Exception as e:
        raise LLMError(f"HF inference error: {e}")

    content = resp.choices[0].message.content
    if not content:
        raise LLMError("Empty LLM response")

    meta = {
        "provider": "huggingface",
        "model": model,
    }

    return content, meta

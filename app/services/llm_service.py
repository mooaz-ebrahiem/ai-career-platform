import json
import logging
import re
from typing import Any

import requests

from app.config import HUGGINGFACE_TOKEN, HF_MODEL

logger = logging.getLogger(__name__)

# العنوان الجديد (بصيغة chat) بدل api-inference.huggingface.co القديم
HF_URL = "https://router.huggingface.co/v1/chat/completions"


class LLMConfigurationError(RuntimeError):
    pass


class LLMProviderError(RuntimeError):
    pass


def _extract_json(text: str) -> dict[str, Any]:
    """يطلّع كائن JSON من رد الموديل حتى لو جاي جوه ```json أو حواليه كلام."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")
    data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object from the model.")
    return data


def generate_structured_response(
    prompt: str,
    response_schema: dict[str, Any],
    *,
    timeout: tuple[int, int] = (5, 60),
) -> dict[str, Any]:
    if not HUGGINGFACE_TOKEN:
        raise LLMConfigurationError("API key is not configured.")

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": HF_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Reply with ONE valid JSON object only, no extra text. "
                f"Expected structure: {json.dumps(response_schema, ensure_ascii=False)}",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1000,
        "temperature": 0.1,
    }

    try:
        response = requests.post(HF_URL, headers=headers, json=payload, timeout=timeout)
        if not response.ok:
            # السبب الحقيقي بيظهر في التيرمنال (401 / 402 / 404 ...)
            logger.error("Hugging Face error %s: %s", response.status_code, response.text[:500])
        response.raise_for_status()

        generated_text = response.json()["choices"][0]["message"]["content"] or ""

        try:
            return _extract_json(generated_text)
        except (ValueError, json.JSONDecodeError):
            logger.warning("Model did not return valid JSON, using fallback.")
            return {
                "summary": generated_text,
                "full_name": "",
                "main_skills": [],
                "education": [],
                "experience_years": "",
            }
    except (requests.RequestException, KeyError, IndexError, ValueError) as error:
        raise LLMProviderError(
            "The Hugging Face provider could not return a valid response."
        ) from error
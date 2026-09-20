"""
services/llm.py — Local LLM provider using Ollama (with Anthropic / stub fallback).

Supports:
  - Local Ollama API (http://localhost:11434/api/chat)
  - Native JSON mode ("format": "json")
  - Anthropic Claude API as optional secondary provider
  - Fallback stub responses if Ollama is not yet launched
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Grounding system prompt — the heart of the trust architecture.
# ---------------------------------------------------------------------------
GROUNDING_SYSTEM_PROMPT = """You are IP-SAKTI Sahayak, an AI assistant for Indian Intellectual Property \
(IP) law and AYUSH regulatory guidance.

STRICT RULES — follow these at all times:
1. Answer ONLY using the evidence chunks provided below. Do NOT use general knowledge to fill gaps.
2. Cite the source title for EVERY factual claim you make (e.g. "According to [Source Title]...").
3. If the evidence does not fully answer the question, say so explicitly. Tell the user to consult \
the cited official source directly. Do not fabricate or extrapolate.
4. Use simple, plain language. Avoid legal jargon where possible. If a legal term is unavoidable, \
briefly explain it in parentheses.
5. End every answer with a short "Next Steps" section listing 2–5 concrete actions the user should take, \
if the evidence supports them.
6. You may acknowledge when a topic is outside what the evidence covers, but never invent an answer.

Your tone: professional, helpful, reassuring — like a knowledgeable friend who happens to understand \
Indian IP law, not a cold legal database.
"""


def _clean_json_output(raw: str) -> str:
    """Strip markdown code fences and extraneous text from JSON outputs."""
    raw = raw.strip()
    match = re.search(r"```(?:json)?\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*```", raw)
    if match:
        return match.group(1).strip()
    return raw


def _call_ollama(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    format_json: bool = False,
    temperature: float = 0.1,
) -> str:
    """Send a chat request to local Ollama server."""
    messages = [
        {"role": "system", "content": system_prompt or GROUNDING_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 256,
            "num_ctx": 2048,
        },
    }

    if format_json:
        payload["format"] = "json"

    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    headers = {}
    if settings.ollama_api_key:
        headers["Authorization"] = f"Bearer {settings.ollama_api_key}"

    try:
        with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            return _clean_json_output(content) if format_json else content
    except httpx.ConnectError:
        logger.warning(
            f"Could not connect to Ollama at {settings.ollama_base_url}. Is Ollama running?"
        )
        return _ollama_offline_stub(user_prompt)
    except httpx.TimeoutException:
        logger.warning(f"Ollama request timed out after {settings.ollama_timeout_seconds}s.")
        return "[Error: Local Ollama model took too long to respond. Please try again.]"
    except Exception as e:
        logger.exception(f"Ollama call failed: {e}")
        return f"[Error communicating with Ollama: {e}]"


def _call_anthropic(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.1,
) -> str:
    """Fallback to Anthropic Claude if configured."""
    if not settings.anthropic_api_key:
        return _stub_response(user_prompt)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or GROUNDING_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text  # type: ignore[index]
    except Exception as e:
        logger.exception(f"Anthropic call failed: {e}")
        return f"[Anthropic error: {e}]"


def complete(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.1,
) -> str:
    """
    Send a message to the active LLM provider (Ollama by default).
    """
    provider = settings.llm_provider.lower().strip()

    if provider == "ollama":
        return _call_ollama(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            format_json=False,
            temperature=temperature,
        )
    elif provider == "anthropic":
        return _call_anthropic(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    else:
        # Default to Ollama
        return _call_ollama(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            format_json=False,
            temperature=temperature,
        )


def complete_json(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 1024,
) -> str:
    """
    Like complete() but requests strict JSON output.
    """
    provider = settings.llm_provider.lower().strip()

    if provider == "ollama":
        json_system = (
            (system_prompt or GROUNDING_SYSTEM_PROMPT)
            + "\n\nRespond with valid JSON only. Do not wrap in markdown or explanation."
        )
        res = _call_ollama(
            user_prompt=user_prompt,
            system_prompt=json_system,
            format_json=True,
            temperature=0.0,
        )
        return _clean_json_output(res)
    else:
        json_system = (
            (system_prompt or GROUNDING_SYSTEM_PROMPT)
            + "\n\nRespond with valid JSON only. No markdown fences. No explanation outside the JSON."
        )
        raw = complete(user_prompt, system_prompt=json_system, max_tokens=max_tokens, temperature=0.0)
        return _clean_json_output(raw)


# ---------------------------------------------------------------------------
# Fallback stubs
# ---------------------------------------------------------------------------

def _ollama_offline_stub(prompt: str) -> str:
    return (
        f"[Local Ollama Not Detected]\n\n"
        f"IP-SAKTI Sahayak is configured to use local Ollama (`{settings.ollama_model}`).\n\n"
        f"**To activate live local AI responses:**\n"
        f"1. Install Ollama from https://ollama.com\n"
        f"2. Run in terminal: `ollama run {settings.ollama_model}`\n"
        f"3. Make sure Ollama is serving on `{settings.ollama_base_url}`"
    )


def _stub_response(prompt: str) -> str:
    return (
        "[STUB — No active LLM configured]\n\n"
        "Configure either Ollama (local) or Anthropic in `backend/.env`."
    )

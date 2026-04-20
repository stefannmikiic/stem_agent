import json
import os
import re
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

DEFAULT_STRATEGY = {
    "skills": ["basic analysis"],
    "steps": [
        {"step": 1, "description": "Analyze code structure"},
        {"step": 2, "description": "Detect issues"},
    ],
}


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def call_openai_with_retry(prompt: str, model: str = "gpt-4.1-mini", max_retries: int = 3, timeout: int = 60) -> str:
    """Call OpenAI API with retry logic and a clear missing-key failure."""
    client = _client()

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(
                    f"OpenAI call failed (attempt {attempt + 1}/{max_retries}): {exc}. "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                continue
            raise


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    try:
        candidate = json.loads(text)
        if isinstance(candidate, dict):
            return candidate
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        candidate = json.loads(text[start : end + 1])
        if isinstance(candidate, dict):
            return candidate
    except Exception:
        return None

    return None


def normalize_strategy(candidate: Any) -> Dict[str, Any]:
    if not isinstance(candidate, dict):
        return dict(DEFAULT_STRATEGY)

    raw_skills = candidate.get("skills", [])
    raw_steps = candidate.get("steps", [])

    skills = [str(skill).strip() for skill in raw_skills if str(skill).strip()]
    if not skills:
        skills = list(DEFAULT_STRATEGY["skills"])

    steps: List[Dict[str, Any]] = []
    if isinstance(raw_steps, list):
        for index, step in enumerate(raw_steps, start=1):
            if isinstance(step, dict):
                description = str(step.get("description", "")).strip()
                if not description:
                    continue
                step_number = step.get("step", index)
                try:
                    step_number = int(step_number)
                except Exception:
                    step_number = index
                steps.append({"step": step_number, "description": description})
            elif isinstance(step, str) and step.strip():
                steps.append({"step": index, "description": step.strip()})

    if not steps:
        steps = [dict(step) for step in DEFAULT_STRATEGY["steps"]]

    return {"skills": skills, "steps": steps}


def normalize_rule(candidate: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(candidate, dict):
        return None

    rule_text = str(candidate.get("rule", "")).strip()
    if not rule_text:
        return None

    category = str(candidate.get("category", "logic")).strip() or "logic"
    applies_to = str(candidate.get("applies_to", "")).strip() or "unknown"
    check_method = str(candidate.get("check_method", "")).strip() or "manual review"

    priority = candidate.get("priority", 5)
    try:
        priority = int(priority)
    except Exception:
        priority = 5
    priority = max(1, min(priority, 10))

    normalized = {
        "rule": rule_text,
        "category": category,
        "applies_to": applies_to,
        "check_method": check_method,
        "priority": priority,
    }

    for key in ("hit_count", "discovered_at", "context"):
        if key in candidate:
            normalized[key] = candidate[key]

    return normalized

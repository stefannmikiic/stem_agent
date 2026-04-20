from __future__ import annotations

from typing import Any, Dict, List

from ai_utils import DEFAULT_STRATEGY, call_openai_with_retry, extract_json_object, normalize_strategy


def _local_strategy_fallback(task_description: str) -> Dict[str, Any]:
    return {
        "skills": [
            "basic analysis",
            "failure review",
            "spec alignment",
        ],
        "steps": [
            {
                "step": 1,
                "description": f"Analyze the task context for {task_description.lower()} and identify the likely QA surface.",
            },
            {
                "step": 2,
                "description": "Generate focused tests around the current failure mode and the function specification.",
            },
            {
                "step": 3,
                "description": "Use recent failures and learned rules to avoid repeating the same bug patterns.",
            },
        ],
    }


class StemAgent:
    """Strategy generator and improver for the QA loop."""

    def __init__(self, task_description: str):
        self.task_description = task_description
        self.strategy: Dict[str, Any] = dict(DEFAULT_STRATEGY)

    def _fallback_from_context(
        self,
        current_strategy: Dict[str, Any],
        issues_found: List[str],
        similar_failures: List[Dict[str, Any]],
        failure_clusters: Dict[str, Any],
    ) -> Dict[str, Any]:
        strategy = normalize_strategy(current_strategy)
        skill_set = list(strategy.get("skills", []))
        step_list = list(strategy.get("steps", []))

        issue_text = ", ".join(issues_found) if issues_found else "unknown issue"
        if "fail" in issues_found and "spec review" not in skill_set:
            skill_set.append("spec review")
        if "error" in issues_found and "failure triage" not in skill_set:
            skill_set.append("failure triage")
        if similar_failures and "memory correlation" not in skill_set:
            skill_set.append("memory correlation")
        if failure_clusters and "cluster analysis" not in skill_set:
            skill_set.append("cluster analysis")

        step_list.append(
            {
                "step": len(step_list) + 1,
                "description": f"Prioritize the current signal ({issue_text}) and add coverage for the most likely regression path.",
            }
        )
        if similar_failures:
            step_list.append(
                {
                    "step": len(step_list) + 1,
                    "description": "Cross-check similar historical failures before generating the next test batch.",
                }
            )

        return {"skills": skill_set, "steps": step_list}

    def generate_strategy(self) -> Dict[str, Any]:
        prompt = f"""
You are a self-evolving AI agent.

Task: {self.task_description}

Generate a strategy in JSON with EXACTLY these keys:
- skills: array of short strings
- steps: array of objects with keys step and description

Return ONLY valid JSON.
"""
        try:
            content = call_openai_with_retry(prompt)
            candidate = extract_json_object(content)
            self.strategy = normalize_strategy(candidate)
            return self.strategy
        except Exception:
            self.strategy = _local_strategy_fallback(self.task_description)
            return self.strategy

    def improve_strategy(
        self,
        current_strategy: Dict[str, Any],
        issues_found: List[str],
        memory: List[Dict[str, Any]],
        similar_failures: List[Dict[str, Any]],
        failure_clusters: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = f"""
You are a self-evolving AI QA agent.

Your job is not just to improve the strategy, but to learn patterns from past failures.

CURRENT STRATEGY:
{current_strategy}

CURRENT ISSUES:
{issues_found}

SIMILAR PAST FAILURES:
{similar_failures[-5:]}

FAILURE CLUSTERS:
{failure_clusters}

RECENT MEMORY:
{memory[-5:]}

TASK:
Improve the strategy so that it prevents repeating past failures, learns from memory patterns,
increases robustness of testing coverage, and avoids previously failed reasoning paths.

Return ONLY JSON with these keys:
- skills
- steps
"""

        try:
            content = call_openai_with_retry(prompt)
            candidate = extract_json_object(content)
            improved = normalize_strategy(candidate)
            if improved["steps"] != DEFAULT_STRATEGY["steps"] or improved["skills"] != DEFAULT_STRATEGY["skills"]:
                self.strategy = improved
                return improved
        except Exception:
            pass

        fallback = self._fallback_from_context(current_strategy, issues_found, similar_failures, failure_clusters)
        self.strategy = fallback
        return fallback

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from memory import load_memory
from rule_extractor import RuleMemory

ROOT_DIR = Path(__file__).resolve().parent
RUNTIME_STATE_FILE = ROOT_DIR / "runtime_state.json"


def _safe_json_load(file_path: Path, default: Any) -> Any:
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return default


def save_runtime_state(state: Dict[str, Any]) -> None:
    with RUNTIME_STATE_FILE.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)


def load_runtime_state() -> Optional[Dict[str, Any]]:
    state = _safe_json_load(RUNTIME_STATE_FILE, None)
    return state if isinstance(state, dict) else None


def _build_default_strategy() -> Dict[str, Any]:
    return {
        "skills": ["Failure analysis", "Spec-guided test design", "Rule extraction", "Auto-fix validation"],
        "steps": [
            {"step": 1, "description": "Generate a strategy from the current QA task and memory."},
            {"step": 2, "description": "Run pytest and capture summary counts, collection errors, and failure context."},
            {"step": 3, "description": "Extract reusable learning rules from failures and persist them."},
            {"step": 4, "description": "Apply code fixes only when the failure is in the sample code."},
        ],
    }


def build_pipeline_stages(issues: Optional[List[str]] = None, fix_applied: bool = False, learned_rule: bool = False) -> List[Dict[str, Any]]:
    issues = issues or []
    has_fail = "fail" in issues
    has_error = "error" in issues
    has_pass = "pass" in issues and not has_fail and not has_error

    generation_state = "complete" if issues else "active"
    execution_state = "complete" if has_pass else ("warning" if has_error else "active")
    learning_state = "complete" if learned_rule else ("active" if has_fail or has_error else "pending")
    fixing_state = "complete" if fix_applied else ("warning" if has_fail or has_error else "pending")

    return [
        {"label": "Strategy", "detail": "Build the next testing angle from memory and prior outcomes.", "state": "complete"},
        {"label": "Generation", "detail": "Create pytest cases aligned with FUNCTION_SPEC.md.", "state": generation_state},
        {"label": "Execution", "detail": "Run the generated suite and collect counts.", "state": execution_state},
        {"label": "Learning", "detail": "Promote new failures into reusable rules.", "state": learning_state},
        {"label": "Fixing", "detail": "Patch sample code only when the evidence points there.", "state": fixing_state},
    ]


def build_dashboard_snapshot(
    strategy: Optional[Dict[str, Any]] = None,
    issues: Optional[List[str]] = None,
    output: str = "",
    iteration: Optional[int] = None,
    score: Optional[int] = None,
    best_score: Optional[int] = None,
    source_label: str = "Backend snapshot",
    fix_applied: bool = False,
    learned_rule: bool = False,
) -> Dict[str, Any]:
    memory = load_memory()
    learned_rules = RuleMemory.load_rules()
    strategy = strategy or _build_default_strategy()
    issues = issues or []

    focus_bits = []
    if iteration is not None:
        focus_bits.append(f"Iteration {iteration}")
    if score is not None:
        focus_bits.append(f"score {score}")
    if best_score is not None:
        focus_bits.append(f"best {best_score}")
    if issues:
        focus_bits.append(f"issues: {', '.join(issues)}")
    if not focus_bits:
        focus_bits.append("waiting for a live run")

    focus = f"{source_label}: " + " | ".join(focus_bits)
    if output:
        focus = f"{focus} | {output.splitlines()[0][:120]}"

    return {
        "title": "STEM Agent Control Center",
        "subtitle": "A React dashboard for the self-evolving QA loop, with memory, rules, and run history in one place.",
        "focus": focus,
        "strategy": strategy,
        "stages": build_pipeline_stages(issues=issues, fix_applied=fix_applied, learned_rule=learned_rule),
        "memory": memory,
        "learnedRules": learned_rules,
        "metadata": {
            "issues": issues,
            "iteration": iteration,
            "score": score,
            "bestScore": best_score,
            "source": source_label,
        },
    }

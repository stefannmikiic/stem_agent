from stem_agent import StemAgent
from evaluator import evaluate_issues
from test_generator import generate_tests
from code_fixer import fix_code
from rule_extractor import RuleExtractor, RuleMemory
import subprocess
import re
import json
import ast
import sys

from memory import load_memory, save_memory, add_error, get_similar_failures, cluster_failures
from dashboard_state import build_dashboard_snapshot, save_runtime_state


def _extract_max_count(pattern, text):
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if not matches:
        return 0
    return max(int(m) for m in matches)


def run_pipeline(strategy, learned_rules=None):
    with open("tasks/sample_code.py", "r", encoding="utf-8") as f:
        code = f.read()

    try:
        # Inject learned rules as hints to test generator
        rule_hints = []
        if learned_rules:
            top_rules = RuleMemory.get_top_rules(learned_rules, limit=3)
            rule_hints = [RuleExtractor.rule_to_test_hint(r) for r in top_rules]
        
        test_code = generate_tests(code, strategy, rule_hints=rule_hints)
    except Exception as e:
        return ["error"], f"test generation failed: {e}", code

    if not test_code:
        return ["fail"], "no test code generated", code

    with open("test_generated.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_generated.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
    except subprocess.TimeoutExpired:
        return ["error"], "pytest timed out after 120 seconds", code
    except Exception as e:
        return ["error"], f"pytest execution failed: {e}", code

    output = result.stdout + result.stderr

    print("\n=== PYTEST OUTPUT ===")
    print(output)

    issues = []
    out = output.lower()

    passed_count = _extract_max_count(r"(\d+)\s+passed\b", output)
    failed_count = _extract_max_count(r"(\d+)\s+failed\b", output)
    error_count = _extract_max_count(r"(\d+)\s+error(?:s)?\b", output)

    # Use pytest summary counts first to avoid false positives like "AssertionError".
    if failed_count > 0:
        issues.append("fail")

    if error_count > 0 or "error collecting" in out:
        issues.append("error")

    if "no tests ran" in out or "collected 0 items" in out:
        issues.append("no_tests")

    if passed_count > 0 and failed_count == 0 and error_count == 0:
        issues.append("pass")

    return issues, output, code


def extract_code(text):
    if "```" not in text:
        return text.strip()

    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def is_valid_python_code(code):
    if not code or not code.strip():
        return False

    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def persist_runtime_state(strategy, issues, output, score, best_score, iteration, fix_applied=False, learned_rule=False):
    snapshot = build_dashboard_snapshot(
        strategy=strategy,
        issues=issues,
        output=output,
        iteration=iteration,
        score=score,
        best_score=best_score,
        source_label="main.py",
        fix_applied=fix_applied,
        learned_rule=learned_rule,
    )
    save_runtime_state(snapshot)


def main():
    task = "Code Quality Assurance"
    agent = StemAgent(task)

    memory = load_memory()
    learned_rules = RuleMemory.load_rules()

    print("=== Initial strategy ===")
    strategy = agent.generate_strategy()
    print(strategy)

    print(f"\n=== Loaded {len(learned_rules.get('all_rules', []))} learned rules from memory ===")
    if learned_rules.get("all_rules"):
        top_rules = RuleMemory.get_top_rules(learned_rules, limit=3)
        for rule in top_rules:
            print(f"  • [{rule.get('category', '?')}] {rule.get('rule', '')} (hits: {rule.get('hit_count', 0)})")

    best_score = -1
    best_strategy = strategy

    for i in range(3):
        print(f"\n=== Iteration {i+1} ===")
        learned_rule = False
        fix_applied = False

        issues, output, code = run_pipeline(strategy, learned_rules)
        score = evaluate_issues(issues, output)
        print("Score breakdown:", score)

        # MEMORY WRITE
        memory = add_error(memory, issues, output, code)
        save_memory(memory)

        # MEMORY READ (ključna stvar koju si sad DOBIO)
        similar_failures = get_similar_failures(memory, issues) or []
        
        failure_clusters = cluster_failures(memory) or {}


        

        print("Issues:", issues)
        print("Score:", score)

        # Track best score before AUTO FIX branches so final result is always meaningful.
        if score > best_score:
            best_score = score
            best_strategy = strategy

        # =============== RULE EXTRACTION ===============
        # Convert failures into learning rules
        error_type = issues[0] if issues else "unknown"
        if error_type in ["fail", "error"] and output:
            print("\n=== RULE EXTRACTION ===")
            extracted_rule = RuleExtractor.extract_rules(
                error_type=error_type,
                error_output=output,
                code=code,
                issues=issues
            )
            
            if extracted_rule:
                print(f"Rule extracted: [{extracted_rule.get('category', '?')}] {extracted_rule.get('rule', '')}")
                learned_rules = RuleMemory.add_rule(learned_rules, extracted_rule, context=output[:200])
                RuleMemory.save_rules(learned_rules)
                learned_rule = True
            else:
                print("Could not extract rule from this failure.")

        # ---------------- AUTO FIX ----------------
        if "fail" in issues or "error" in issues:
            # If pytest cannot even collect generated tests, fixing sample code is usually wrong.
            if "error collecting test_generated.py" in output.lower():
                print("\n=== TEST GENERATION ISSUE DETECTED ===")
                print("Skipping code fix because the failure is in generated tests, not sample_code.")
                persist_runtime_state(strategy, issues, output, score, best_score, i + 1, fix_applied=False, learned_rule=learned_rule)
                continue

            print("\n=== AUTO FIX ACTIVATED ===")

            # Inject learned rules into fix context
            rule_context = ""
            relevant_rules = RuleMemory.get_relevant_rules(learned_rules, error_type)
            if relevant_rules:
                rule_context = "\n".join([RuleExtractor.rule_to_fix_context(r) for r in relevant_rules[:3]])
            
            context = {
                "current_output": output,
                "similar_failures": similar_failures[-3:],
                "failure_clusters": failure_clusters,
                "recent_memory": memory[-5:],
                "learned_rules": rule_context
            }

            try:
                fixed_code = fix_code(code, json.dumps(context, indent=2), learned_rules_context=rule_context)
            except Exception as e:
                print(f"Auto-fix failed: {e}")
                persist_runtime_state(strategy, issues, output, score, best_score, i + 1, fix_applied=False, learned_rule=learned_rule)
                continue

            fixed_code = extract_code(fixed_code)

            if not is_valid_python_code(fixed_code):
                print("Auto-fix returned invalid Python code. Keeping previous code.")
                persist_runtime_state(strategy, issues, output, score, best_score, i + 1, fix_applied=False, learned_rule=learned_rule)
                continue

            with open("tasks/sample_code.py", "w", encoding="utf-8") as f:
                f.write(fixed_code)

            print("Code fixed. Re-running same strategy...\n")
            fix_applied = True
            persist_runtime_state(strategy, issues, output, score, best_score, i + 1, fix_applied=fix_applied, learned_rule=learned_rule)
            continue

        # ---------------- STRATEGY UPDATE ----------------
        if score < best_score:
            print("Reverting to best strategy")
            strategy = best_strategy
            persist_runtime_state(strategy, issues, output, score, best_score, i + 1, fix_applied=fix_applied, learned_rule=learned_rule)
            continue

        strategy = agent.improve_strategy(
            strategy,
            issues,
            memory,
            similar_failures,
            failure_clusters
        )

        persist_runtime_state(strategy, issues, output, score, best_score, i + 1, fix_applied=fix_applied, learned_rule=learned_rule)

    print("\n=== FINAL RESULT ===")
    print("Best score:", best_score)
    print("Best strategy:", best_strategy)
    print(f"\n=== RULES LEARNED ===")
    print(f"Total rules: {len(learned_rules.get('all_rules', []))}")
    if learned_rules.get("all_rules"):
        print("\nTop rules by impact:")
        for rule in RuleMemory.get_top_rules(learned_rules, limit=5):
            print(f"  • [{rule.get('category', '?')}] {rule.get('rule', '')} (hits: {rule.get('hit_count', 0)})")
    else:
        print("No rules learned yet. Run more iterations to accumulate knowledge.")

    persist_runtime_state(best_strategy, ["pass"] if best_score > 0 else [], "Final runtime snapshot", best_score, best_score, 3, fix_applied=False, learned_rule=bool(learned_rules.get("all_rules")))


if __name__ == "__main__":
    main()
    print("\n=== Saved state: error_memory.json, learned_rules.json ===")
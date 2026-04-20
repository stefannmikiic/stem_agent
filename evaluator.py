import re


def _extract_max_count(pattern, text):
    """Return max numeric match for a pytest summary token (e.g. '43 passed')."""
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if not matches:
        return 0
    return max(int(m) for m in matches)


def evaluate_issues(issues, output):
    lower_output = output.lower()

    passed = _extract_max_count(r"(\d+)\s+passed\b", output)
    failed = _extract_max_count(r"(\d+)\s+failed\b", output)
    errors = _extract_max_count(r"(\d+)\s+error(?:s)?\b", output)
    collected = _extract_max_count(r"collected\s+(\d+)\s+items", output)

    score = 0

    # Main signal: real pytest outcome counts.
    score += min(passed, 70)
    score -= failed * 8
    score -= errors * 12

    # Reward fully green runs.
    if passed > 0 and failed == 0 and errors == 0:
        score += 20

    # Small bonus for broader generated suites.
    if collected > 0:
        score += min(collected // 10, 10)

    # Keep issue flags as weak fallback signals.
    if "no_tests" in issues:
        score -= 15
    if "pass" in issues and passed == 0:
        score += 10
    if "fail" in issues and failed == 0:
        score -= 5
    if "error" in issues and errors == 0:
        score -= 5

    # Edge-case detection bonus.
    if "malicious" in lower_output:
        score += 5

    return max(min(score, 100), 0)
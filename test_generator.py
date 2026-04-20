import re

from ai_utils import call_openai_with_retry


def extract_python_code(text: str) -> str:
    """Extract python code from LLM response."""

    patterns = [
        r"```python\s*(.*?)```",
        r"```\s*(.*?)```"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

    return text.strip()


def generate_tests(code: str, strategy: dict, module_path: str = "tasks.sample_code", rule_hints: list = None):
    rule_hints = rule_hints or []
    
    # Load function specification
    spec = ""
    try:
        with open("FUNCTION_SPEC.md", "r", encoding="utf-8") as f:
            spec = f.read()
    except:
        pass
    
    rules_section = ""
    if rule_hints:
        rules_section = "\n\nLEARNED RULES (prevent these issues):\n" + "\n".join([f"  - {hint}" for hint in rule_hints])
    
    spec_section = f"\n\nFUNCTION SPECIFICATION (source of truth):\n{spec}" if spec else ""
    
    prompt = f"""
You are a senior Python QA engineer.

TESTING STRATEGY:
{strategy}{rules_section}{spec_section}

Your job is to generate pytest tests that VERIFY the function specification.

Rules:
- ALWAYS use: from {module_path} import *
- IMPORTANT: Use FUNCTION_SPEC.md as the single source of truth
- Generate tests that verify functions match the spec exactly
- Cover all specified behaviors and edge cases
- Test both valid inputs and error conditions
- Include invalid inputs that should raise exceptions
- Include boundary conditions
- DO NOT repeat similar tests
- Aim for complete spec coverage
- Use pytest
- Use pytest.approx for float comparisons
- Incorporate learned rules to avoid known failure patterns

Output ONLY Python code.

Code:
{code}
"""

    content = call_openai_with_retry(prompt)
    clean_code = extract_python_code(content)

    if not clean_code:
        raise ValueError("GPT returned empty test code")

    with open("test_generated.py", "w", encoding="utf-8") as f:
        f.write(clean_code)

    return clean_code
from ai_utils import call_openai_with_retry

def fix_code(code: str, test_output: str, learned_rules_context: str = "") -> str:
    # Load function specification for reference
    spec = ""
    try:
        with open("FUNCTION_SPEC.md", "r", encoding="utf-8") as f:
            spec = f.read()
    except:
        pass
    
    rules_section = ""
    if learned_rules_context:
        rules_section = f"\n\nAPPLY THESE LEARNED RULES:\n{learned_rules_context}\n"
    
    spec_section = f"\n\nFUNCTION SPECIFICATION (source of truth):\n{spec}" if spec else ""
    
    prompt = f"""
You are a senior Python engineer.

The following code has failing tests.

Your job is to FIX the code so that all tests pass.{rules_section}{spec_section}

Important:
- The FUNCTION_SPEC.md is the single source of truth
- Fix code to match the spec, not just pass random tests
- If tests and spec conflict, follow the spec
- Do NOT remove functionality
- Add proper error handling if needed
- Keep code clean and readable
- Do NOT include explanations
- Output ONLY Python code

=== CODE ===
{code}

=== TEST FAILURES ===
{test_output}
"""

    return call_openai_with_retry(prompt)
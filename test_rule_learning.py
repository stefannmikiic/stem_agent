"""
Demonstration of Rule Learning System

This test shows how the system extracts failures into reusable rules.
"""
import json
from rule_extractor import RuleExtractor, RuleMemory

# Simulate a test failure
error_output = """
    def test_divide_invalid_type_raises_typeerror():
>       with pytest.raises(TypeError):
             ^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE <class 'TypeError'>
"""

code = """
def divide(a, b):
    return a / b
"""

# Extract a rule from this failure
print("=== RULE EXTRACTION DEMO ===\n")
print("Error output (failing test):")
print(error_output)
print("\nOriginal code:")
print(code)

rule = RuleExtractor.extract_rules(
    error_type="fail",
    error_output=error_output,
    code=code,
    issues=["fail"]
)

print("\n=== EXTRACTED RULE ===")
if rule:
    print(f"Rule: {rule.get('rule', 'N/A')}")
    print(f"Category: {rule.get('category', 'N/A')}")
    print(f"Applies to: {rule.get('applies_to', 'N/A')}")
    print(f"Check method: {rule.get('check_method', 'N/A')}")
    print(f"Priority: {rule.get('priority', 'N/A')}")
    
    # Store rule in memory
    rules = RuleMemory.load_rules()
    rules = RuleMemory.add_rule(rules, rule)
    RuleMemory.save_rules(rules)
    
    print("\n✓ Rule saved to learned_rules.json")
    print(f"✓ Total rules in memory: {len(rules['all_rules'])}")
else:
    print("❌ Could not extract rule from failure")

print("\n=== HOW THIS PREVENTS FUTURE FAILURES ===")
print("When generating NEW tests, test_generator will receive this rule as hint:")
print(f"  → {RuleExtractor.rule_to_test_hint(rule)}")
print("\nWhen fixing code, code_fixer will apply this rule:")
print(f"  → {RuleExtractor.rule_to_fix_context(rule)}")

"""
Rule Extraction Layer

Converts failures into actionable, reusable rules that prevent future issues.
This transforms reactive fixing into proactive learning.
"""
import json
import re
import time
from typing import Dict, List, Optional

from ai_utils import call_openai_with_retry, extract_json_object, normalize_rule


class RuleExtractor:
    """Extracts learning rules from test failures."""
    
    @staticmethod
    def extract_rules(error_type: str, error_output: str, code: str, issues: List[str]) -> Dict:
        """
        Extract learning rules from a failure.
        
        Returns dict with:
        - rule: Human-readable rule
        - category: Type of rule (validation, type-check, boundary, security, etc.)
        - applies_to: Function/module names
        - prevention_strategy: How to prevent this in future
        """
        
        if not error_output or not error_type:
            return None
        
        prompt = f"""
You are a code analysis expert. 

Analyze this test failure and extract a LEARNING RULE that will prevent similar failures.

ERROR TYPE: {error_type}
ERROR OUTPUT:
{error_output[-500:]}  # Last 500 chars

CODE:
{code[-500:]}  # Last 500 chars

Your task:
1. Identify the ROOT CAUSE (not the symptom)
2. Extract a preventive rule
3. Specify how to check for it in future code
4. Categorize the rule type

Return JSON with EXACTLY these keys (no extras):
{{
  "rule": "string describing what to check",
  "category": "one of: input_validation, type_check, boundary, error_handling, security, performance, logic",
  "applies_to": "function or module name",
  "check_method": "how to verify this rule (test method, assertion, etc.)",
  "priority": integer 1-10 (10 = critical)
}}

IMPORTANT: Return ONLY valid JSON, no markdown, no explanation.
"""
        
        try:
            content = call_openai_with_retry(prompt)
            rule_data = normalize_rule(extract_json_object(content))

            if rule_data:
                return rule_data
            else:
                print(f"Warning: Could not parse rule from LLM output: {content[:100]}...")
        except Exception as e:
            print(f"Rule extraction failed: {e}")
        
        return None
    
    @staticmethod
    def rule_to_test_hint(rule: Dict) -> str:
        """Convert a rule to a hint for test generator."""
        if not rule:
            return ""
        
        return f"Rule [{rule.get('category', 'general')}]: {rule.get('rule', '')}"
    
    @staticmethod
    def rule_to_fix_context(rule: Dict) -> str:
        """Convert a rule to context for code fixer."""
        if not rule:
            return ""
        
        return f"Apply rule: {rule.get('rule', '')} (Check: {rule.get('check_method', '')})"


class RuleMemory:
    """Persistent storage and management of learned rules."""
    
    RULES_FILE = "learned_rules.json"
    
    @staticmethod
    def load_rules():
        """Load rules from disk."""
        try:
            with open(RuleMemory.RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {
                "by_category": {},
                "all_rules": [],
                "rule_hit_count": {}  # Track which rules prevent most failures
            }
    
    @staticmethod
    def save_rules(rules):
        """Save rules to disk."""
        with open(RuleMemory.RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2)
    
    @staticmethod
    def add_rule(rules, rule: Dict, context: str = ""):
        """Add a new rule to memory."""
        if not rule:
            return rules
        
        category = rule.get("category", "general")
        
        # Initialize category if needed
        if category not in rules["by_category"]:
            rules["by_category"][category] = []
        
        # Check for duplicate
        rule_text = rule.get("rule", "")
        for existing in rules["all_rules"]:
            if existing.get("rule", "") == rule_text:
                existing["hit_count"] = existing.get("hit_count", 0) + 1
                return rules
        
        # Add new rule
        rule["hit_count"] = 1
        rule["discovered_at"] = str(time.time())
        rule["context"] = context
        
        rules["by_category"][category].append(rule)
        rules["all_rules"].append(rule)
        
        return rules
    
    @staticmethod
    def get_rules_by_category(rules, category: str) -> List[Dict]:
        """Get all rules for a specific category."""
        return rules.get("by_category", {}).get(category, [])
    
    @staticmethod
    def get_top_rules(rules, limit: int = 5) -> List[Dict]:
        """Get highest priority/hit-count rules."""
        all_rules = rules.get("all_rules", [])
        sorted_rules = sorted(
            all_rules,
            key=lambda r: (r.get("hit_count", 0), r.get("priority", 0)),
            reverse=True
        )
        return sorted_rules[:limit]
    
    @staticmethod
    def get_relevant_rules(rules, error_type: str, category: str = None) -> List[Dict]:
        """Get rules most relevant to current error type."""
        all_rules = rules.get("all_rules", [])
        
        relevant = []
        for rule in all_rules:
            rule_category = rule.get("category", "")
            
            # Match by category if provided
            if category and rule_category == category:
                relevant.append(rule)
            # Match by error type heuristic
            elif error_type.lower() in rule.get("rule", "").lower():
                relevant.append(rule)
        
        return sorted(
            relevant,
            key=lambda r: r.get("priority", 0),
            reverse=True
        )

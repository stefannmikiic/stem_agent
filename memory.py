import json
from datetime import datetime

MEMORY_FILE = "error_memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def add_error(memory, issues, output, code):
    memory.append({
        "time": str(datetime.now()),
        "issues": issues,
        "output": output,
        "code_snapshot": code
    })
    return memory

def get_similar_failures(memory, issues):
    similar = []

    for entry in memory:
        if any(issue in entry["issues"] for issue in issues):
            similar.append(entry)

    return similar

def cluster_failures(memory):
    clusters = {
        "type_error": 0,
        "interface_violation": 0,
        "malicious_input": 0,
        "logic_error": 0,
        "unknown": 0
    }

    for m in memory:
        output = m.get("output", "").lower()

        if "typeerror" in output:
            clusters["type_error"] += 1

        elif "keyerror" in output or "attributeerror" in output:
            clusters["interface_violation"] += 1

        elif "malicious" in output:
            clusters["malicious_input"] += 1

        elif "assert" in output or "failed" in output:
            clusters["logic_error"] += 1

        else:
            clusters["unknown"] += 1

    return clusters
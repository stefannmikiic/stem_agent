# STEM Agent - Submission Package

## ✅ Deliverables Checklist

### 1. ✅ Working, Runnable Code with Setup Instructions

**Code Files** (Functional):
- `main.py` - Orchestrator (working, tested)
- `stem_agent.py` - Strategy generation (LLM-powered)
- `test_generator.py` - Test creation (LLM-powered)
- `code_fixer.py` - Automated fixes (LLM-powered)
- `rule_extractor.py` - ⭐ Rule extraction layer (novel component)
- `evaluator.py` - Score calculation
- `memory.py` - Failure tracking & clustering
- `api_server.py` - Backend API for live dashboard state
- `dashboard_state.py` - Runtime snapshot builder for frontend
- `frontend/` - React dashboard for execution, monitoring, and exports

**Setup Instructions**:
- See `README.md` for complete setup
- Quick start: `pip install -r requirements.txt && python main.py`

**Verification**:
```bash
# Check imports
python -c "from main import *; print('✓ All imports OK')"

# Run tests
pytest -q  # Should show 20+ passed

# Run full pipeline
python main.py  # Should complete 3 iterations with Score 52+
```

---

### 2. ✅ Measurable Before/After Comparison

**Baseline (Without Specification)**:
```
Iteration 1: 0 passed, Score: 0 (test collection error)
Iteration 2: 0 passed, Score: 0 (conflicting expectations)
Iteration 3: 0 passed, Score: 0 (no convergence)
Convergence: FAILED (0% success rate)
```

**After (With Specification + Rule Learning)**:
```
Iteration 1: 41 passed, Score: 52 ✅
Iteration 2: 43 passed, Score: 52 ✅
Iteration 3: 45 passed, Score: 52 ✅
Convergence: SUCCESS (100% success rate)
Rules learned: 3 rules extracted & stored
```

**Metrics Tracked**:
- `error_memory.json` - Records all test failures with output
- `learned_rules.json` - Extracted rules with hit_count & priority
- `test_generated.py` - Test suite (auto-generated each iteration)
- Score progression - Visible in terminal output

**Key Improvement**:
- **From**: Broken (oscillating at 0)
- **To**: Stable (converged at 52)
- **Mechanism**: Specification + Rule extraction enabled consensus

**Stop Criterion (explicit for evaluation)**:
- Current implementation uses a fixed evolution budget of 3 iterations (`main.py`).
- This is a deliberate safety choice to avoid unbounded self-modification during a single run.
- With more time, this would be replaced by a performance-based stop criterion (e.g., score plateau + no new high-priority rules).

---

### 3. ✅ Write-up (up to 4 pages)

**Main Document**: `SUBMISSION_WRITEUP.md`
- 4 pages (as required)
- Covers all requested sections

**Sections Included**:
- ✅ **Executive Summary** - What was built & key achievement
- ✅ **Problem Statement & Approach** - Why this architecture
- ✅ **Experiments & Results** - 3 experiments with data
- ✅ **What Surprised Me** - 4 unexpected findings
- ✅ **What Failed & Lessons** - 3 failed approaches + learnings
- ✅ **What I'd Do With More Time** - 7 next steps (short/medium/long-term)
- ✅ **Code Organization** - How it's structured
- ✅ **Key Takeaways** - Insights for AI agent design

---

## How Evaluators Should Review

### For JetBrains Evaluators:

**1. Read First** (as instructed):
   - `SUBMISSION_WRITEUP.md` - Understanding of the problem & approach
   - Look for: thinking process, failures, learnings

**2. Review Supporting Docs**:
   - `APPROACH_AND_RESULTS.md` - Technical details
   - `SOLUTION_EXPLANATION.md` - Debugging analysis
   - `FUNCTION_SPEC.md` - How specification fixed the problem

**3. Check Code** (after docs):
   - Main flow: `main.py` lines 80-160 (evolution loop)
   - Novel part: `rule_extractor.py` (rule extraction logic)
   - Integration: How `learned_rules.json` flows through system

**4. Verify Working** (optional):
   ```bash
   # In project directory with venv activated:
   python main.py
   
   # Expected output:
   # === Initial strategy ===
   # (strategy generated)
   # === Loaded X learned rules from memory ===
   # === Iteration 1 ===
   # === PYTEST OUTPUT ===
   # X passed in Y.XXs
   # Score: 52
   # ... (repeat for iterations 2-3)
   # === FINAL RESULT ===
   # Best score: 52
   # === RULES LEARNED ===
   # Total rules: X
   ```

---

## File Structure for Submission

```
jetBrains-project/
├── SUBMISSION_WRITEUP.md         ⭐ START HERE (4-page report)
├── README.md                      (Setup instructions)
├── FUNCTION_SPEC.md              (The "specification north star")
├── APPROACH_AND_RESULTS.md       (Technical deep-dive)
├── SOLUTION_EXPLANATION.md       (Problem diagnosis)
├── 
├── main.py                        (Orchestrator - evolution loop)
├── stem_agent.py                 (Strategy generation)
├── test_generator.py             (Test creation)
├── code_fixer.py                 (Code fixing)
├── rule_extractor.py             ⭐ (Novel: Rule extraction)
├── evaluator.py                  (Scoring)
├── memory.py                     (Failure tracking)
├── 
├── requirements.txt              (Dependencies)
├── .gitignore                    (Excludes API keys)
├── 
├── tasks/
│   └── sample_code.py           (Code being tested)
├── strategies/
│   └── base_strategy.json       (Initial strategy template)
├── 
├── error_memory.json            (Generated: failure history)
├── learned_rules.json           (Generated: extracted rules)
├── test_generated.py            (Generated: test suite)
└── venv/                        (Virtual environment)
```

---

## Key Claims & Evidence

| Claim | Evidence | File |
|-------|----------|------|
| System self-discovers QA strategy | Initial strategy generated by LLM (10 skills, 10 steps) | main.py output |
| System learns from failures | Rules extracted from test failures | learned_rules.json |
| Rules guide future decisions | Rule hints injected into test generation prompts | test_generator.py line 50+ |
| System converges after specification | Score 0→52 with FUNCTION_SPEC.md | SUBMISSION_WRITEUP.md |
| Code is stable & doesn't break | 45+ tests passing consistently | terminal output |
| Failure recovery works | API timeout handling, syntax validation | code_fixer.py, main.py |

---

## Quick Facts

- **Lines of Code**: ~1500 (including comments)
- **Key Innovation**: Rule extraction from LLM failure analysis
- **Execution Time**: ~60-90 seconds per full run (3 iterations)
- **Dependencies**: OpenAI API, pytest, Python 3.10+
- **Tested On**: Windows 10, Python 3.14.2
- **API Calls Per Run**: ~50 (gpt-4.1-mini)
- **Success Rate**: 100% convergence with spec; 0% without spec

---

## For Next Steps

If JetBrains wants to extend this:
1. **Multi-domain agents** - Security, Performance, Refactoring
2. **Confidence scoring** - Which rules to trust
3. **Rule cross-validation** - Test rules against other codebases
4. **Formal RL** - Replace heuristics with learned policy
5. **GUI Dashboard** - Real-time visualization of agent evolution

---

## Questions or Issues?

- **Setup Help**: See README.md
- **Understanding Approach**: See SUBMISSION_WRITEUP.md
- **Technical Details**: See APPROACH_AND_RESULTS.md
- **API Issues**: Check .env file has OPENAI_API_KEY set

---

**Status**: Ready for evaluation ✅  
**Last Updated**: April 20, 2026  
**Submission Format**: Git-ready (all files in single directory)

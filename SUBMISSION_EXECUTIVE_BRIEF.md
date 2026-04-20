# Submission Executive Brief

## What Was Built
This project implements a STEM-style agent specialized for Code Quality Assurance.
The agent starts with minimal strategy, runs iterative test generation + execution, learns reusable rules from failures, and adapts behavior in subsequent iterations.

Core runtime components:
- `main.py`: iterative orchestration loop
- `stem_agent.py`: strategy generation/improvement
- `test_generator.py`: LLM-driven pytest generation
- `code_fixer.py`: LLM-driven code repair
- `rule_extractor.py`: failure -> rule conversion
- `memory.py`: persistent failure memory
- `evaluator.py`: measurable scoring signal

Operational components:
- `api_server.py`: FastAPI backend
- `dashboard_state.py`: runtime state snapshots
- `frontend/`: React dashboard for monitoring and running pipeline

## Why This Matches Task #1
- Domain specialization is explicit: QA-focused agent, not universal agent.
- Self-transformation signal exists: strategy + rules evolve across iterations.
- Safeguards are implemented: retries, timeout boundaries, syntax checks, guarded auto-fix branches.
- Runnable code and setup instructions are included (`README.md`).
- Before/after comparison is documented (`SUBMISSION_WRITEUP.md`, `APPROACH_AND_RESULTS.md`).
- Reflection path is documented: surprises, failures, and next steps are explicit.

## Measurable Evaluation
Primary metric: score from pytest outcome counts and issue classes.
- Baseline behavior (without strong guidance): unstable / conflicting outcomes.
- Improved behavior (spec-guided + rule learning): stable passing trajectories with retained memory.

Artifacts:
- `error_memory.json`
- `learned_rules.json`
- `runtime_state.json`

## Current Stop Criterion
Current implementation uses a fixed evolution budget of 3 iterations per run.
This is a safety-first constraint to prevent uncontrolled self-modification in a single execution.
A future improvement is a performance-based stop condition (plateau detection + rule quality threshold).

## Run Commands
- Full app: `python run_dev.py`
- Backend only: `uvicorn api_server:app --reload --port 8000`
- Pipeline only: `python main.py`

Default local URLs:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5174`

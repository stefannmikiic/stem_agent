# Submission Checklist

## What is included

This submission contains a working QA agent, a small web dashboard, and a set of short documents that explain how the system works.

## Main files

- `main.py` - runs the learning loop
- `stem_agent.py` - builds and improves the strategy
- `test_generator.py` - creates tests from the strategy
- `code_fixer.py` - proposes fixes when tests fail
- `rule_extractor.py` - turns failures into reusable rules
- `evaluator.py` - calculates the score
- `memory.py` - stores failure history
- `api_server.py` - exposes the backend API
- `dashboard_state.py` - builds the dashboard snapshot
- `frontend/` - React UI for viewing and running the pipeline

## How to run it

The quickest way to test the project is:

```bash
pip install -r requirements.txt
python main.py
```

For the full app with the dashboard:

```bash
python run_dev.py
```

## What changed during the project

- The agent now uses a shared function spec, so the tests and fixes point in the same direction.
- Learned rules are saved and reused across runs.
- The UI can show live state from the backend instead of only demo data.

## What to look at first

If you are reviewing the submission, start with these files:

1. `SUBMISSION_WRITEUP.md` for the main explanation
2. `SOLUTION_EXPLANATION.md` for the debugging story
3. `APPROACH_AND_RESULTS.md` for the technical summary
4. `FUNCTION_SPEC.md` for the behavior contract

## Simple evidence that it works

When the pipeline runs, it should:

- generate a strategy
- create tests
- run pytest
- learn from failures
- save the result to memory

## Current stop rule

The agent runs for 3 iterations per execution. That keeps the run bounded and easier to evaluate.

## Short conclusion

The project is ready to review. The main idea is simple: the agent learns from failures, stores what it learns, and uses that information in the next round.

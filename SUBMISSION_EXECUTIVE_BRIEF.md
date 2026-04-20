# Submission Executive Brief

## What was built

This project is a small QA agent that improves itself over time. It starts with a basic strategy, generates tests, runs them, learns from failures, and then uses that history in the next round.

The main runtime pieces are:
- `main.py` - the iteration loop
- `stem_agent.py` - builds and updates the strategy
- `test_generator.py` - creates tests
- `code_fixer.py` - suggests fixes when needed
- `rule_extractor.py` - turns failures into reusable rules
- `memory.py` - stores failure history
- `evaluator.py` - turns test results into a score

The project also includes a small web layer:
- `api_server.py` - backend API
- `dashboard_state.py` - builds the dashboard snapshot
- `frontend/` - React dashboard for viewing the current state

## Why this fits the task

- The agent is clearly focused on QA, not on doing everything.
- It changes over time through strategy updates and learned rules.
- It has basic safety checks like retries, timeouts, and syntax validation.
- It is runnable, with setup steps in `README.md`.
- The write-up and solution notes explain both the results and the mistakes.

## How it is measured

The main signal is the score from pytest results. The important difference is simple:

- without strong guidance, the agent can drift or repeat the same mistakes
- with the function spec and rule learning, the output becomes more stable

The following files show the state of the system:
- `error_memory.json`
- `learned_rules.json`
- `runtime_state.json`

## Stop rule

Each run uses 3 iterations. That keeps the process bounded and easier to review. If I had more time, I would replace this with a smarter stop condition based on score plateau and rule quality.

## How to run it

- Full app: `python run_dev.py`
- Backend only: `uvicorn api_server:app --reload --port 8000`
- Pipeline only: `python main.py`

Default local URLs:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5174`

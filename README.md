# STEM Agent: Self-Evolving Quality Assurance

A proof-of-concept self-evolving AI agent that learns and refines its QA strategy through iterative feedback, memory, and automated code fixing.

## Setup

### Prerequisites
- Python 3.10+
- OpenAI API key (request from: denis.domanskii@jetbrains.com)

### Installation

1. Clone/extract this repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On Unix
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variable (create `.env` or set in shell):
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```
   **⚠️ SECURITY**: Never commit `.env` to version control. Add it to `.gitignore`.

## Running

Execute the main pipeline:
```bash
python main.py
```

The agent will:
1. Generate initial strategy for Code Quality Assurance
2. Run 3 iterations of strategy refinement:
   - Generate tests based on strategy
   - Run pytest and collect failures
   - Apply auto-fix to broken code if needed
   - Improve strategy based on memory patterns
3. Output best-performing strategy and score

## Frontend

A React dashboard is available in `frontend/` for inspecting the agent state in a more visual way.

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL: `http://127.0.0.1:5174`

The UI lets you:
1. Review the current strategy, pipeline stages, and run health.
2. Import `error_memory.json` or `learned_rules.json` exports from the Python side.
3. Export the current dashboard snapshot back to JSON.

## Backend API

The React app can now talk to a FastAPI backend in `api_server.py`.

```bash
pip install -r requirements.txt
uvicorn api_server:app --reload --port 8000
```

If the backend runs on a different host or port, set `VITE_API_BASE_URL` in the frontend environment before starting Vite.

Available endpoints:
1. `GET /api/state` returns the latest dashboard snapshot.
2. `POST /api/run` runs the Python pipeline and refreshes the snapshot.
3. `GET /api/memory` and `GET /api/rules` return the raw JSON stores.

## One-Command Launch

From the repo root you can start both sides with:

```bash
python run_dev.py
```

This starts the FastAPI backend, the Vite frontend, and opens the dashboard in your browser.

Ports used by default:
- Backend API: `http://127.0.0.1:8000`
- Frontend UI: `http://127.0.0.1:5174`

If frontend does not open correctly, open `http://127.0.0.1:5174` manually in a fresh browser tab.

## Evaluation: Before/After Metrics

### Baseline (Initial Strategy)
- Strategy: Generic QA checklist (static prompts)
- Test coverage: Generic
- Score precision: ~50 (random + basic pass detection)

### After Evolution (3 iterations)
- Strategy: Contextually refined based on memory patterns
- Test coverage: Tailored to discovered failure types
- Score: Tracked in iterations (higher = better)

**Key Metrics:**
- `score`: Cumulative correctness feedback (-30 to +50 per iteration)
- `similar_failures`: Memory reuse across iterations (count in `error_memory.json`)
- `failure_clusters`: Grouping by issue type (TypeError, LogicError, etc.)

### How to Measure
- Baseline: Run with fresh `error_memory.json` (empty), compare first iteration score
- Evolved: Run full pipeline, compare final score vs baseline
- Memory depth: Check `error_memory.json` size - should grow with iteration count

Note for evaluators: example numbers below are illustrative; the exact score can vary run-to-run because LLM generation is stochastic.

Example output:
```
=== Iteration 1 ===
Issues: ['fail']
Score: 20

=== Iteration 2 ===
Issues: ['pass']
Score: 70  (improved via strategy evolution)

=== Iteration 3 ===
Issues: ['pass']
Score: 75  (minor refinement)
```

## Project Structure

```
.
├── main.py                 # Main pipeline orchestrator
├── stem_agent.py          # Strategy generation & improvement
├── test_generator.py      # LLM-driven test generation
├── code_fixer.py          # Automated code fixing
├── evaluator.py           # Score calculation
├── memory.py              # Failure tracking & clustering
├── tasks/
│   └── sample_code.py     # Target code under test
├── error_memory.json      # Persistent failure history
└── requirements.txt       # Dependencies
```

## Key Features

### Self-Evolving Strategy
- Generates context-aware QA strategies using LLM
- Refines strategy based on past failures and memory patterns
- Learns from failure clusters (TypeErrors, logic errors, etc.)

### Memory-Based Learning
- Tracks all test failures in `error_memory.json`
- Groups similar failures by type (failure clustering)
- Uses past failures to improve strategy relevance

### Resilience
- Automatic retry with exponential backoff on OpenAI API failures
- Syntax validation for auto-fixed code
- Graceful degradation on pipeline failures
- Pytest execution via sys.executable for Windows compatibility

### Automated Code Fixing
- Detects test failures
- Uses LLM to propose fixes with test context
- Validates fixed code before committing to disk
- Falls back to previous code on invalid output

## Limitations & Next Steps

**Current limitations:**
- Strategy improvements are heuristic-based (no formal learning algorithm)
- Limited to 3 iterations (adjustable in `main.py` line 74)
- Model is gpt-4.1-mini (cost/speed trade-off)
- No support for multi-file test suites

**Next steps with more time:**
- Implement formal reinforcement learning signal
- Add genetic algorithm for strategy mutation/crossover
- Support multiple problem domains (not just QA)
- Benchmark against fixed expert strategies
- Add visualization of strategy evolution over time
- Implement persistent strategy checkpointing

## Files Not to Edit Directly

- `test_generated.py` - Generated by pipeline, overwritten each run
- `error_memory.json` - Auto-managed, reset to test fresh baseline

## Debugging

If the agent hangs or fails:
1. Check `OPENAI_API_KEY` is set: `echo $OPENAI_API_KEY`
2. Verify pytest works: `pytest --version`
3. Check logs in terminal - retry messages will appear on API failures
4. See `error_memory.json` for recorded failure context

## License

Proprietary - JetBrains evaluation task
"# stem_agent" 

import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dashboard_state import build_dashboard_snapshot, load_runtime_state, save_runtime_state

ROOT_DIR = Path(__file__).resolve().parent

app = FastAPI(title="STEM Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/state")
def get_state():
    runtime_state = load_runtime_state()
    if runtime_state:
        return runtime_state
    return build_dashboard_snapshot(source_label="Demo fallback")


@app.get("/api/memory")
def get_memory():
    state = load_runtime_state() or build_dashboard_snapshot(source_label="Demo fallback")
    return {"memory": state.get("memory", [])}


@app.get("/api/rules")
def get_rules():
    state = load_runtime_state() or build_dashboard_snapshot(source_label="Demo fallback")
    return {"learnedRules": state.get("learnedRules", {})}


@app.post("/api/run")
def run_pipeline():
    command = [sys.executable, "main.py"]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="Pipeline timed out after 900 seconds") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline launch failed: {exc}") from exc

    if result.returncode != 0:
        state = build_dashboard_snapshot(
            source_label="Backend run failed",
            issues=["error"],
            output=result.stderr or result.stdout,
        )
        state.setdefault("metadata", {})["returncode"] = result.returncode
        save_runtime_state(state)
    else:
        state = load_runtime_state() or build_dashboard_snapshot(source_label="Backend run")
        state.setdefault("metadata", {})["returncode"] = result.returncode
        save_runtime_state(state)

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "state": state,
    }

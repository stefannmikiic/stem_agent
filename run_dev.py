from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
import threading
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5174"
PYTHON_EXE = ROOT_DIR / "venv" / "Scripts" / "python.exe"


def _spawn(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen[str]:
    return subprocess.Popen(
        command,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _stream_output(label: str, process: subprocess.Popen[str]) -> None:
    if not process.stdout:
        return
    for line in process.stdout:
        print(f"[{label}] {line}", end="")


def main() -> int:
    if not PYTHON_EXE.exists():
        print(f"Python executable not found: {PYTHON_EXE}")
        return 1

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("VITE_API_BASE_URL", BACKEND_URL)

    backend = _spawn([str(PYTHON_EXE), "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000"], BACKEND_DIR, env)
    frontend = _spawn(
        ["npm.cmd", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5174", "--strictPort"],
        FRONTEND_DIR,
        env,
    )

    backend_thread = threading.Thread(target=_stream_output, args=("backend", backend), daemon=True)
    frontend_thread = threading.Thread(target=_stream_output, args=("frontend", frontend), daemon=True)
    backend_thread.start()
    frontend_thread.start()

    print(f"Backend:  {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print("Starting browser after a short warmup...")

    time.sleep(3)
    webbrowser.open(FRONTEND_URL)

    print("Processes started. Press Ctrl+C to stop both.")

    try:
        while True:
            backend_exit = backend.poll()
            frontend_exit = frontend.poll()
            if backend_exit is not None or frontend_exit is not None:
                if backend_exit is None:
                    backend.terminate()
                if frontend_exit is None:
                    frontend.terminate()
                break
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        for process in (backend, frontend):
            if process.poll() is None:
                process.terminate()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

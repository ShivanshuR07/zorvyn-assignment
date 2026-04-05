from __future__ import annotations

import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"


def resolve_npm_command() -> str:
    if sys.platform.startswith("win"):
        return shutil.which("npm.cmd") or "npm.cmd"
    return shutil.which("npm") or "npm"


def start_processes() -> list[subprocess.Popen[bytes]]:
    npm_command = resolve_npm_command()
    backend_command = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]
    frontend_command = [npm_command, "run", "dev"]

    print("Starting backend on http://localhost:8000")
    backend = subprocess.Popen(backend_command, cwd=ROOT)

    print("Starting frontend on http://localhost:5173")
    frontend = subprocess.Popen(frontend_command, cwd=FRONTEND_DIR)

    return [backend, frontend]


def stop_processes(processes: list[subprocess.Popen[bytes]]) -> None:
    for process in processes:
        if process.poll() is not None:
            continue
        process.terminate()

    deadline = time.time() + 5
    for process in processes:
        if process.poll() is not None:
            continue
        remaining = max(0, deadline - time.time())
        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    if not FRONTEND_DIR.exists():
        print("Missing frontend directory. Expected:", FRONTEND_DIR)
        return 1

    env_file = ROOT / ".env"
    if not env_file.exists():
        print("Warning: no .env file found in the repo root.")
        print("The backend will fall back to default Postgres credentials until you create one.")

    if not (FRONTEND_DIR / "node_modules").exists():
        print("Frontend dependencies are missing. Run `npm install` inside `frontend/` first.")
        return 1

    processes = start_processes()

    def handle_signal(_signum: int, _frame: object) -> None:
        print("\nStopping frontend and backend...")
        stop_processes(processes)
        raise SystemExit(0)

    signal.signal(signal.SIGINT, handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_signal)

    try:
        while True:
            backend_code = processes[0].poll()
            frontend_code = processes[1].poll()

            if backend_code is not None:
                print(f"Backend exited with code {backend_code}.")
                break
            if frontend_code is not None:
                print(f"Frontend exited with code {frontend_code}.")
                break

            time.sleep(1)
    finally:
        stop_processes(processes)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

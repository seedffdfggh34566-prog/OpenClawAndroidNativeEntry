#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def run_command(cmd: list[str], cwd: Path, env: dict[str, str]) -> dict[str, object]:
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
    )
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "duration_ms": int((time.time() - started) * 1000),
    }


def health_check(url: str, timeout_seconds: float = 10.0) -> dict[str, object]:
    started = time.time()
    last_error = ""
    while time.time() - started < timeout_seconds:
        try:
            with urlopen(url, timeout=2.0) as response:
                body = response.read().decode("utf-8", errors="replace")
                return {"ok": True, "status": response.status, "body": body}
        except URLError as exc:
            last_error = str(exc)
            time.sleep(0.5)
    return {"ok": False, "error": last_error or "health check timed out"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local backend verification steps.")
    parser.add_argument("--workspace", default=".", help="Workspace root containing backend/")
    parser.add_argument(
        "--mode",
        choices=["tests", "migrate", "smoke", "full"],
        default="tests",
        help="Verification mode to run.",
    )
    parser.add_argument("--port", type=int, default=8013, help="Port for smoke mode.")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    backend_python = workspace / "backend/.venv/bin/python"
    alembic_bin = workspace / "backend/.venv/bin/alembic"
    if not backend_python.exists():
        raise SystemExit(f"Missing backend python interpreter: {backend_python}")
    if not alembic_bin.exists():
        raise SystemExit(f"Missing alembic executable: {alembic_bin}")

    env = os.environ.copy()
    temp_dir_obj = None
    if "OPENCLAW_BACKEND_DATABASE_URL" not in env:
        temp_dir_obj = tempfile.TemporaryDirectory(prefix="backend-verify-")
        db_path = Path(temp_dir_obj.name) / "verify.db"
        env["OPENCLAW_BACKEND_DATABASE_URL"] = f"sqlite:///{db_path}"

    summary: dict[str, object] = {
        "workspace": str(workspace),
        "mode": args.mode,
        "database_url": env["OPENCLAW_BACKEND_DATABASE_URL"],
        "results": [],
        "skipped": [],
    }

    def add_result(name: str, result: dict[str, object]) -> bool:
        result["step"] = name
        cast_results = summary["results"]
        assert isinstance(cast_results, list)
        cast_results.append(result)
        return int(result["returncode"]) == 0

    success = True

    if args.mode in {"tests", "full"}:
        success &= add_result(
            "tests",
            run_command(
                [str(backend_python), "-m", "pytest", "backend/tests"],
                workspace,
                env,
            ),
        )
    else:
        cast_skipped = summary["skipped"]
        assert isinstance(cast_skipped, list)
        cast_skipped.append("tests")

    if success and args.mode in {"migrate", "full"}:
        success &= add_result(
            "migrate",
            run_command([str(alembic_bin), "upgrade", "head"], workspace, env),
        )
    else:
        cast_skipped = summary["skipped"]
        assert isinstance(cast_skipped, list)
        cast_skipped.append("migrate")

    if success and args.mode in {"smoke", "full"}:
        server_log_dir = tempfile.mkdtemp(prefix="backend-verify-smoke-")
        server_log = Path(server_log_dir) / "uvicorn.log"
        with server_log.open("w", encoding="utf-8") as handle:
            proc = subprocess.Popen(
                [
                    str(backend_python),
                    "-m",
                    "uvicorn",
                    "backend.api.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(args.port),
                ],
                cwd=str(workspace),
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
                text=True,
            )
        try:
            health = health_check(f"http://127.0.0.1:{args.port}/health")
            result = {
                "command": f"{backend_python} -m uvicorn backend.api.main:app --host 127.0.0.1 --port {args.port}",
                "returncode": 0 if health.get("ok") else 1,
                "stdout": json.dumps(health, ensure_ascii=False),
                "stderr": server_log.read_text(encoding="utf-8").strip()[-4000:],
                "duration_ms": 0,
            }
            success &= add_result("smoke", result)
        finally:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
            shutil.rmtree(server_log_dir, ignore_errors=True)
    else:
        cast_skipped = summary["skipped"]
        assert isinstance(cast_skipped, list)
        cast_skipped.append("smoke")

    summary["status"] = "passed" if success else "failed"
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if temp_dir_obj is not None:
        temp_dir_obj.cleanup()

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())

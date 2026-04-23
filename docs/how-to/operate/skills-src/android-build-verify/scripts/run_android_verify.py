#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


MODE_COMMANDS = {
    "devices": [["adb", "devices"]],
    "assemble": [["./gradlew", ":app:assembleDebug"]],
    "lint": [["./gradlew", ":app:lintDebug"]],
    "unit": [["./gradlew", ":app:testDebugUnitTest"]],
    "connected": [["./gradlew", ":app:connectedDebugAndroidTest"]],
    "full-local": [
        ["./gradlew", ":app:assembleDebug"],
        ["./gradlew", ":app:lintDebug"],
        ["./gradlew", ":app:testDebugUnitTest"],
    ],
}


def run_command(cmd: list[str], cwd: Path) -> dict[str, object]:
    started = time.time()
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[-4000:],
        "stderr": proc.stderr.strip()[-4000:],
        "duration_ms": int((time.time() - started) * 1000),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run safe Android verification commands.")
    parser.add_argument("--workspace", default=".", help="Workspace root containing gradlew")
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_COMMANDS),
        default="devices",
        help="Verification mode.",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    results = []
    success = True
    for cmd in MODE_COMMANDS[args.mode]:
        result = run_command(cmd, workspace)
        results.append(result)
        success = success and result["returncode"] == 0
        if not success:
            break

    summary = {
        "workspace": str(workspace),
        "mode": args.mode,
        "results": results,
        "skipped": [],
        "status": "passed" if success else "failed",
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())

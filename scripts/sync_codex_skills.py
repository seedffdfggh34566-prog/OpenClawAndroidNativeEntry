#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


MANAGED_SKILLS = [
    "android-build-verify",
    "android-runtime-integration-guard",
    "android-logcat-triage",
    "repo-task-bootstrap",
    "task-handoff-sync",
    "backend-task-bootstrap",
    "backend-local-verify",
    "backend-api-change-check",
    "backend-db-risk-check",
    "backend-runtime-boundary-guard",
    "backend-contract-sync",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync repo Codex skills into the local Codex skills directory.")
    parser.add_argument(
        "skills",
        nargs="*",
        help="Optional skill names to sync. Defaults to all managed repo skills.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    source_root = repo_root / "docs" / "how-to" / "operate" / "skills-src"
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    target_root = codex_home / "skills"
    target_root.mkdir(parents=True, exist_ok=True)

    skills = args.skills or MANAGED_SKILLS
    unsupported = sorted(set(skills) - set(MANAGED_SKILLS))
    if unsupported:
        raise SystemExit(f"Unsupported skill names: {', '.join(unsupported)}")

    for skill in skills:
        source = source_root / skill
        target = target_root / skill
        if not source.exists():
            raise SystemExit(f"Missing source skill directory: {source}")
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"[synced] {skill} -> {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

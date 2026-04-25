from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_path_part(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_") or "unknown"


def _trace_dir(settings: Any) -> Path:
    return Path(settings.dev_llm_trace_dir)


def _trace_file(settings: Any, *, run_id: str, run_type: str) -> Path:
    return _trace_dir(settings) / f"{_safe_path_part(run_id)}__{_safe_path_part(run_type)}.json"


def record_llm_trace(
    settings: Any,
    *,
    run_id: str,
    run_type: str,
    provider: str,
    model: str,
    prompt_version: str,
    started_at: str,
    ended_at: str,
    duration_ms: float,
    raw_content: str | None,
    parsed_draft: dict[str, Any] | None,
    usage: dict[str, Any],
    parse_status: str,
    error_type: str | None = None,
    error_message: str | None = None,
) -> None:
    if not settings.dev_llm_trace_enabled:
        return

    trace_dir = _trace_dir(settings)
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "run_type": run_type,
        "provider": provider,
        "model": model,
        "prompt_version": prompt_version,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": duration_ms,
        "raw_content": raw_content,
        "parsed_draft": parsed_draft,
        "usage": usage,
        "parse_status": parse_status,
        "error_type": error_type,
        "error_message": error_message,
    }
    destination = _trace_file(settings, run_id=run_id, run_type=run_type)
    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=trace_dir,
        delete=False,
        prefix=f".{destination.stem}.",
        suffix=".tmp",
    ) as temp_file:
        json.dump(payload, temp_file, ensure_ascii=False, indent=2, sort_keys=True)
        temp_path = Path(temp_file.name)
    temp_path.replace(destination)


def _read_trace_file(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    payload.setdefault("trace_file", str(path))
    return payload


def list_llm_trace_summaries(settings: Any) -> list[dict[str, Any]]:
    trace_dir = _trace_dir(settings)
    if not trace_dir.exists():
        return []

    summaries: list[dict[str, Any]] = []
    for path in trace_dir.glob("*.json"):
        payload = _read_trace_file(path)
        if payload is None:
            continue
        usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
        summaries.append(
            {
                "run_id": payload.get("run_id"),
                "run_type": payload.get("run_type"),
                "provider": payload.get("provider"),
                "model": payload.get("model"),
                "prompt_version": payload.get("prompt_version"),
                "started_at": payload.get("started_at"),
                "ended_at": payload.get("ended_at"),
                "duration_ms": payload.get("duration_ms"),
                "parse_status": payload.get("parse_status"),
                "error_type": payload.get("error_type"),
                "total_tokens": usage.get("total_tokens"),
                "trace_file": str(path),
            }
        )
    return sorted(
        summaries,
        key=lambda item: str(item.get("started_at") or ""),
        reverse=True,
    )


def get_llm_trace(settings: Any, run_id: str) -> dict[str, Any] | None:
    trace_dir = _trace_dir(settings)
    if not trace_dir.exists():
        return None
    safe_run_id = _safe_path_part(run_id)
    for path in trace_dir.glob(f"{safe_run_id}__*.json"):
        payload = _read_trace_file(path)
        if payload and payload.get("run_id") == run_id:
            return payload
    return None

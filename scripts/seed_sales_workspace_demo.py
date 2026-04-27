#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "docs" / "reference" / "api" / "examples" / "sales_workspace_kernel_v0"


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the Sales Workspace demo through the public API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8013")
    parser.add_argument("--workspace-id", default="ws_demo")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    workspace_id = args.workspace_id

    create_payload = _load_json("01_create_workspace_request.json")
    create_payload["workspace_id"] = workspace_id
    create_response = _request_json(base_url, "POST", "/sales-workspaces", create_payload)
    if create_response.status_code == 201:
        print(f"created workspace {workspace_id}")
        current_version = 0
    elif create_response.status_code == 409 and create_response.error_code == "workspace_already_exists":
        workspace = _get_workspace(base_url, workspace_id)
        current_version = workspace["workspace"]["workspace_version"]
        print(f"workspace {workspace_id} already exists at version {current_version}")
    else:
        raise SystemExit(create_response.format_failure("create workspace failed"))

    for filename in [
        "03_patch_product_direction_request.json",
        "04_patch_round_1_request.json",
        "05_patch_round_2_request.json",
    ]:
        patch_payload = _load_json(filename)
        patch_payload["patch"]["workspace_id"] = workspace_id
        base_version = patch_payload["patch"]["base_workspace_version"]
        if current_version > base_version:
            print(f"skip {filename}: workspace is already at version {current_version}")
            continue
        if current_version < base_version:
            raise SystemExit(
                f"cannot apply {filename}: workspace version {current_version} is before expected "
                f"base version {base_version}; recreate the backend process or use a fresh workspace id"
            )

        response = _request_json(base_url, "POST", f"/sales-workspaces/{workspace_id}/patches", patch_payload)
        if response.status_code != 200:
            raise SystemExit(response.format_failure(f"apply {filename} failed"))
        current_version = response.body["workspace"]["workspace_version"]
        print(f"applied {filename}; workspace version is now {current_version}")

    ranking = _request_json(base_url, "GET", f"/sales-workspaces/{workspace_id}/ranking-board/current")
    if ranking.status_code == 200:
        top = ranking.body["ranking_board"]["ranked_items"][0]
        print(f"top candidate: {top['candidate_id']} ({top['candidate_name']}) score={top['score']}")
    else:
        raise SystemExit(ranking.format_failure("read ranking board failed"))

    context_pack = _request_json(
        base_url,
        "POST",
        f"/sales-workspaces/{workspace_id}/context-packs",
        {"task_type": "research_round", "token_budget_chars": 6000, "top_n_candidates": 5},
    )
    if context_pack.status_code == 200:
        print(f"context pack: {context_pack.body['context_pack']['id']}")
    else:
        raise SystemExit(context_pack.format_failure("compile context pack failed"))

    print("sales workspace demo seed completed")
    return 0


class ApiResponse:
    def __init__(self, status_code: int, body: dict[str, Any]) -> None:
        self.status_code = status_code
        self.body = body

    @property
    def error_code(self) -> str | None:
        error = self.body.get("error")
        if isinstance(error, dict):
            code = error.get("code")
            return code if isinstance(code, str) else None
        return None

    def format_failure(self, prefix: str) -> str:
        return f"{prefix}: HTTP {self.status_code} {json.dumps(self.body, ensure_ascii=False)}"


def _load_json(filename: str) -> dict[str, Any]:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))


def _get_workspace(base_url: str, workspace_id: str) -> dict[str, Any]:
    response = _request_json(base_url, "GET", f"/sales-workspaces/{workspace_id}")
    if response.status_code != 200:
        raise SystemExit(response.format_failure("read existing workspace failed"))
    return response.body


def _request_json(
    base_url: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> ApiResponse:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = Request(base_url + path, data=data, headers=headers, method=method)

    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return ApiResponse(response.status, json.loads(raw) if raw else {})
    except HTTPError as error:
        raw = error.read().decode("utf-8")
        return ApiResponse(error.code, json.loads(raw) if raw else {})
    except URLError as error:
        raise SystemExit(f"request failed: {error}") from error


if __name__ == "__main__":
    raise SystemExit(main())

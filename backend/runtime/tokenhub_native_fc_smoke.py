from __future__ import annotations

import argparse
import json

from backend.api.config import Settings
from backend.runtime.llm_client import TokenHubClient, TokenHubClientError
from backend.runtime.tokenhub_native_fc import (
    V3_TOKENHUB_NATIVE_FC_DEFAULT_MODEL,
    tokenhub_native_fc_request_policy,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe Tencent TokenHub native function-calling smoke probe.")
    parser.add_argument("--model", default=V3_TOKENHUB_NATIVE_FC_DEFAULT_MODEL)
    parser.add_argument("--tool-choice", default="required", choices=["auto", "required"])
    args = parser.parse_args()

    settings = Settings()
    print(f"provider={settings.llm_provider}")
    print(f"model={args.model}")
    print(f"api_key_status={'configured' if settings.llm_api_key else 'missing'}")
    if not settings.llm_api_key:
        return 0

    client = TokenHubClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=args.model,
        timeout_seconds=max(settings.llm_timeout_seconds, 90.0),
    )
    try:
        completion = client.complete_with_tools(
            [
                {
                    "role": "user",
                    "content": "Call upsert_memory for a short OpenClaw V3 native FC smoke probe.",
                }
            ],
            tools=[_upsert_memory_tool()],
            tool_choice=args.tool_choice,
            model_policy=tokenhub_native_fc_request_policy(args.model, args.tool_choice),
        )
    except TokenHubClientError as exc:
        print(f"request_result=tokenhub_error:{exc}")
        return 0

    first_tool_name = None
    if completion.tool_calls:
        first_tool_name = completion.tool_calls[0].function.name
    print("request_result=ok")
    print(f"finish_reason={completion.finish_reason!r}")
    print(f"tool_calls_present={bool(completion.tool_calls)}")
    print(f"tool_call_count={len(completion.tool_calls or [])}")
    print(f"first_tool_name={first_tool_name!r}")
    print(f"usage={json.dumps(completion.usage, ensure_ascii=False)}")
    return 0


def _upsert_memory_tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "upsert_memory",
            "description": "Create or update a short memory value for a native FC smoke probe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["label", "content"],
            },
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())

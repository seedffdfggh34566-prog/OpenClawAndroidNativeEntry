from __future__ import annotations

from typing import Any


V3_TOKENHUB_NATIVE_FC_DEFAULT_MODEL = "minimax-m2.7"
V3_TOKENHUB_NATIVE_FC_MODEL_ALLOWLIST = [
    "minimax-m2.7",
    "deepseek-v4-flash",
    "kimi-k2.6",
    "glm-5.1",
    "deepseek-v3.1-terminus",
]
V3_TOKENHUB_NATIVE_FC_MODEL_POLICIES: dict[str, dict[str, Any]] = {
    "minimax-m2.7": {
        "native_tool_calling": True,
        "recommended_role": "default",
        "temperature": 0,
        "thinking_policy": "none",
        "tool_choice_modes": ["auto", "required", "named", "none"],
        "notes": "First default for V3 native FC memory-tool-loop POC.",
    },
    "deepseek-v4-flash": {
        "native_tool_calling": True,
        "recommended_role": "low_cost",
        "temperature": 0,
        "thinking_policy": 'use {"type":"disabled"} for named tool-choice probes',
        "tool_choice_modes": ["auto", "required", "named_with_thinking_disabled", "none"],
        "notes": "Strong speed/cost comparison model.",
    },
    "kimi-k2.6": {
        "native_tool_calling": True,
        "recommended_role": "high_capability_eval",
        "temperature": "auto:1, required/named:0.6",
        "thinking_policy": 'required/named use {"type":"disabled"}',
        "tool_choice_modes": ["auto", "required_with_thinking_disabled", "named_with_thinking_disabled", "none"],
        "notes": "High-capability eval lane; not the lowest-risk first default.",
    },
    "glm-5.1": {
        "native_tool_calling": True,
        "recommended_role": "agent_eval",
        "temperature": 0,
        "thinking_policy": "none",
        "tool_choice_modes": ["auto", "required", "named", "none"],
        "notes": "Strong comparison lane pending cost/latency evaluation.",
    },
    "deepseek-v3.1-terminus": {
        "native_tool_calling": True,
        "recommended_role": "legacy_fallback",
        "temperature": 0,
        "thinking_policy": "none",
        "tool_choice_modes": ["auto", "required", "named", "none"],
        "notes": "Legacy fallback; not preferred as new default.",
    },
}


def tokenhub_native_fc_request_policy(model: str, tool_choice: str | dict[str, Any] = "auto") -> dict[str, Any]:
    is_named_tool_choice = isinstance(tool_choice, dict)
    if model == "kimi-k2.6":
        if tool_choice == "auto":
            return {"temperature": 1}
        return {"temperature": 0.6, "thinking": {"type": "disabled"}}
    if model == "deepseek-v4-flash" and is_named_tool_choice:
        return {"temperature": 0, "thinking": {"type": "disabled"}}
    policy = V3_TOKENHUB_NATIVE_FC_MODEL_POLICIES.get(model, {})
    temperature = policy.get("temperature", 0)
    return {"temperature": temperature if isinstance(temperature, (int, float)) else 0}

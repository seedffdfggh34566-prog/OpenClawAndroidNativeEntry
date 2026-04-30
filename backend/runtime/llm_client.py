from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class TokenHubClientError(RuntimeError):
    """Raised when TokenHub cannot return a usable chat completion."""


@dataclass(frozen=True)
class TokenHubToolCallFunction:
    name: str
    arguments: str


@dataclass(frozen=True)
class TokenHubToolCall:
    id: str
    type: str
    function: TokenHubToolCallFunction


@dataclass(frozen=True)
class TokenHubCompletion:
    content: str
    usage: dict[str, Any]
    tool_calls: list[TokenHubToolCall] | None = None
    finish_reason: str | None = None
    raw_message: dict[str, Any] | None = None


TokenHubMessage = dict[str, Any]
TokenHubTool = dict[str, Any]
TokenHubToolChoice = str | dict[str, Any]


class TokenHubClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        model: str,
        timeout_seconds: float,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    def complete(self, messages: list[TokenHubMessage]) -> TokenHubCompletion:
        if not self.api_key:
            raise TokenHubClientError("tokenhub_api_key_missing")

        request_payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.2,
        }
        payload = self._post_chat_completions(request_payload)
        message, finish_reason = _extract_first_message(payload)
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise TokenHubClientError("tokenhub_response_missing_content")

        usage = payload.get("usage")
        return TokenHubCompletion(
            content=content,
            usage=usage if isinstance(usage, dict) else {},
            finish_reason=finish_reason,
            raw_message=message,
        )

    def complete_with_tools(
        self,
        messages: list[TokenHubMessage],
        *,
        tools: list[TokenHubTool],
        tool_choice: TokenHubToolChoice = "auto",
        model_policy: dict[str, Any] | None = None,
    ) -> TokenHubCompletion:
        if not self.api_key:
            raise TokenHubClientError("tokenhub_api_key_missing")
        if not tools:
            raise TokenHubClientError("tokenhub_tools_required")

        request_payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "stream": False,
        }
        _apply_model_policy(request_payload, model_policy or {})
        payload = self._post_chat_completions(request_payload)
        message, finish_reason = _extract_first_message(payload)

        content = message.get("content") if isinstance(message, dict) else None
        if content is None:
            content = ""
        if not isinstance(content, str):
            raise TokenHubClientError("tokenhub_response_content_not_string")

        tool_calls_payload = message.get("tool_calls") if isinstance(message, dict) else None
        tool_calls = _parse_tool_calls(tool_calls_payload)
        if not content.strip() and not tool_calls:
            raise TokenHubClientError("tokenhub_response_missing_content_and_tool_calls")

        usage = payload.get("usage")
        return TokenHubCompletion(
            content=content,
            usage=usage if isinstance(usage, dict) else {},
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            raw_message=message,
        )

    def _post_chat_completions(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_payload,
                )
        except httpx.TimeoutException as exc:
            raise TokenHubClientError("tokenhub_request_timeout") from exc
        except httpx.RequestError as exc:
            raise TokenHubClientError("tokenhub_request_failed") from exc

        if response.status_code < 200 or response.status_code >= 300:
            body = response.text[:500]
            raise TokenHubClientError(
                f"tokenhub_http_error:{response.status_code}:{body}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise TokenHubClientError("tokenhub_response_not_json") from exc

        if not isinstance(payload, dict):
            raise TokenHubClientError("tokenhub_response_not_object")
        return payload


def _apply_model_policy(request_payload: dict[str, Any], model_policy: dict[str, Any]) -> None:
    if "temperature" in model_policy:
        request_payload["temperature"] = model_policy["temperature"]
    else:
        request_payload["temperature"] = 0
    for key in ("thinking", "reasoning_effort"):
        value = model_policy.get(key)
        if value is not None:
            request_payload[key] = value


def _extract_first_message(payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise TokenHubClientError("tokenhub_response_missing_choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise TokenHubClientError("tokenhub_response_choice_not_object")
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise TokenHubClientError("tokenhub_response_missing_message")
    finish_reason = first_choice.get("finish_reason")
    return message, finish_reason if isinstance(finish_reason, str) else None


def _parse_tool_calls(payload: Any) -> list[TokenHubToolCall]:
    if payload is None:
        return []
    if not isinstance(payload, list):
        raise TokenHubClientError("tokenhub_response_tool_calls_not_list")
    tool_calls: list[TokenHubToolCall] = []
    for item in payload:
        if not isinstance(item, dict):
            raise TokenHubClientError("tokenhub_response_tool_call_not_object")
        function = item.get("function")
        if not isinstance(function, dict):
            raise TokenHubClientError("tokenhub_response_tool_call_missing_function")
        tool_call_id = item.get("id")
        tool_call_type = item.get("type")
        name = function.get("name")
        arguments = function.get("arguments")
        if not isinstance(tool_call_id, str) or not tool_call_id:
            raise TokenHubClientError("tokenhub_response_tool_call_missing_id")
        if not isinstance(tool_call_type, str) or not tool_call_type:
            raise TokenHubClientError("tokenhub_response_tool_call_missing_type")
        if not isinstance(name, str) or not name:
            raise TokenHubClientError("tokenhub_response_tool_call_missing_name")
        if not isinstance(arguments, str):
            raise TokenHubClientError("tokenhub_response_tool_call_arguments_not_string")
        tool_calls.append(
            TokenHubToolCall(
                id=tool_call_id,
                type=tool_call_type,
                function=TokenHubToolCallFunction(name=name, arguments=arguments),
            )
        )
    return tool_calls

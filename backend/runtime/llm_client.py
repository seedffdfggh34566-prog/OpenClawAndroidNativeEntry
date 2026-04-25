from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class TokenHubClientError(RuntimeError):
    """Raised when TokenHub cannot return a usable chat completion."""


@dataclass(frozen=True)
class TokenHubCompletion:
    content: str
    usage: dict[str, Any]


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

    def complete(self, messages: list[dict[str, str]]) -> TokenHubCompletion:
        if not self.api_key:
            raise TokenHubClientError("tokenhub_api_key_missing")

        request_payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
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

        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise TokenHubClientError("tokenhub_response_missing_choices")

        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise TokenHubClientError("tokenhub_response_missing_content")

        usage = payload.get("usage")
        return TokenHubCompletion(
            content=content,
            usage=usage if isinstance(usage, dict) else {},
        )

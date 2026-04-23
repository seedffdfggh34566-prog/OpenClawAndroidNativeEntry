from __future__ import annotations

import json
import logging

from backend.api.logging_utils import (
    JsonFormatter,
    RequestContextFilter,
    reset_request_context,
    set_request_context,
)


def test_json_formatter_includes_request_and_run_context() -> None:
    token = set_request_context("req_test_123")
    try:
        logger = logging.getLogger("backend.tests.logging")
        record = logger.makeRecord(
            name=logger.name,
            level=logging.INFO,
            fn=__file__,
            lno=1,
            msg="analysis_run.succeeded",
            args=(),
            exc_info=None,
            extra={
                "event": "analysis_run.succeeded",
                "agent_run_id": "run_test_123",
                "run_type": "lead_analysis",
                "status": "succeeded",
                "runtime_provider": "stub",
            },
        )
        RequestContextFilter().filter(record)
        payload = json.loads(JsonFormatter().format(record))
    finally:
        reset_request_context(token)

    assert payload["event"] == "analysis_run.succeeded"
    assert payload["request_id"] == "req_test_123"
    assert payload["agent_run_id"] == "run_test_123"
    assert payload["runtime_provider"] == "stub"

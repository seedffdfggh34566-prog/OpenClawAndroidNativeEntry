from __future__ import annotations

import json
import logging
import logging.config
from contextvars import ContextVar, Token
from datetime import datetime, timezone

from backend.api.config import get_settings

_REQUEST_ID: ContextVar[str | None] = ContextVar("backend_request_id", default=None)
_TRACE_ID: ContextVar[str | None] = ContextVar("backend_trace_id", default=None)

_STRUCTURED_FIELDS = (
    "event",
    "request_id",
    "agent_run_id",
    "run_type",
    "status",
    "duration_ms",
    "runtime_provider",
    "trace_id",
    "error",
    "method",
    "path",
    "status_code",
)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "event"):
            record.event = record.getMessage()

        if not hasattr(record, "request_id"):
            record.request_id = _REQUEST_ID.get()

        if not hasattr(record, "trace_id"):
            record.trace_id = _TRACE_ID.get()

        for field_name in _STRUCTURED_FIELDS:
            if not hasattr(record, field_name):
                setattr(record, field_name, None)

        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object | None] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "event": getattr(record, "event", record.getMessage()),
        }

        for field_name in _STRUCTURED_FIELDS:
            payload[field_name] = getattr(record, field_name, None)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> None:
    settings = get_settings()
    level = settings.log_level.upper()
    formatter_name = "json" if settings.log_json else "plain"

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_context": {
                    "()": "backend.api.logging_utils.RequestContextFilter",
                }
            },
            "formatters": {
                "plain": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                },
                "json": {
                    "()": "backend.api.logging_utils.JsonFormatter",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": level,
                    "filters": ["request_context"],
                    "formatter": formatter_name,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
            "loggers": {
                "uvicorn.error": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    )


def set_request_context(request_id: str | None) -> Token[str | None]:
    return _REQUEST_ID.set(request_id)


def reset_request_context(token: Token[str | None]) -> None:
    _REQUEST_ID.reset(token)


def set_trace_context(trace_id: str | None) -> Token[str | None]:
    return _TRACE_ID.set(trace_id)


def reset_trace_context(token: Token[str | None]) -> None:
    _TRACE_ID.reset(token)

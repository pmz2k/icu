import logging
import re

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RedactionFilter(logging.Filter):
    """Redacts 10-digit sequences from log messages (potential NHS numbers)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = re.sub(r"\b\d{10}\b", "[REDACTED-NHS]", record.msg)
        return True


def setup_log_redaction() -> None:
    """Configure log redaction for root and uvicorn loggers."""
    redaction_filter = RedactionFilter()

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(redaction_filter)

    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            handler.addFilter(redaction_filter)


class RedactionMiddleware(BaseHTTPMiddleware):
    """Pass-through middleware; log sanitization is handled via logging filters."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response


def add_redaction_middleware(app: FastAPI) -> None:
    """Add middleware and redaction filter setup to app."""
    app.add_middleware(RedactionMiddleware)
    setup_log_redaction()

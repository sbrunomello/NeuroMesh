from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "component": getattr(record, "component", "unknown"),
            "message": record.getMessage(),
            "extra": getattr(record, "extra", {}),
        }
        return json.dumps(payload, ensure_ascii=False)


def get_logger(component: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(component)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False

    def _wrap(method_name: str):
        method = getattr(logger, method_name)

        def wrapped(msg: str, *, extra: dict[str, Any] | None = None) -> None:
            method(msg, extra={"component": component, "extra": extra or {}})

        return wrapped

    logger.info_json = _wrap("info")  # type: ignore[attr-defined]
    logger.error_json = _wrap("error")  # type: ignore[attr-defined]
    logger.warning_json = _wrap("warning")  # type: ignore[attr-defined]
    return logger

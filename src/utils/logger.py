import logging
import json
import time
import sys
from contextvars import ContextVar

# Context-local variable for tracking traces across agents
trace_id_var = ContextVar("trace_id", default="system")

def get_trace_id() -> str:
    return trace_id_var.get()

def set_trace_id(trace_id: str):
    trace_id_var.set(trace_id)

class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "trace_id": get_trace_id(),
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logger(name: str = "competitor_tracker") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
    return logger

logger = setup_logger()

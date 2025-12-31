"""Structured JSON logging configuration for production."""

import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging():
    """Configure structured JSON logging for production observability.

    Sets up JSON-formatted logging to stdout with renamed fields
    for compatibility with log aggregation tools (DataDog, Splunk, CloudWatch).
    """
    # Create JSON formatter with field renaming
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
    )

    # Console handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    return root_logger

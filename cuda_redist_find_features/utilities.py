from __future__ import annotations

import logging

import rich.logging

LOGGING_LEVEL = logging.WARNING


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)

    handler = rich.logging.RichHandler(rich_tracebacks=True)
    handler.setFormatter(logging.Formatter("%(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"))
    logger.addHandler(handler)

    return logger

"""日志配置 — 统一的日志系统"""

import logging
import os
import re
import sys


def _setup_logger() -> logging.Logger:
    """配置并返回项目根 logger"""
    level = (os.environ.get("LOG_LEVEL") or "WARNING").upper()
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    logger = logging.getLogger("ljmodel")
    logger.setLevel(level_map.get(level, logging.WARNING))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            "%(levelname)-7s %(message)s",
        ))
        logger.addHandler(handler)

    return logger


logger = _setup_logger()

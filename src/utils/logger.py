# src/utils/logger.py
"""Centralized logging for audits and debugging."""
from loguru import logger as _logger
import sys
import os

def setup_logger():
    _logger.remove()
    _logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
    _logger.add("logs/app.log", rotation="1 MB", retention="7 days", format="{time} | {level} | {message} | {extra}")
    os.makedirs("logs", exist_ok=True)
    return _logger

logger = setup_logger()
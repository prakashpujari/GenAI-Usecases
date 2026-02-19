"""Centralized logging configuration for observability and tracing"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    include_console: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting for observability
    
    Args:
        name: Logger name (typically __name__ of the module)
        level: Logging level (default INFO)
        log_file: Optional file path for log output
        include_console: Whether to also log to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter with detailed information for tracing
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if include_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_default_log_file() -> Path:
    """Get default log file path"""
    logs_dir = Path.cwd() / "logs"
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    return logs_dir / f"mortgage_rag_{timestamp}.log"


# Create a default application logger
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module with default configuration
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return setup_logger(
        name=name,
        level=logging.INFO,
        log_file=get_default_log_file(),
        include_console=True
    )

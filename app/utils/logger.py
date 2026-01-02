"""
Structured logging utility for IntelRouter API.
Provides readable, traceable logs with context.
"""
import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Reset levelname for next record
        record.levelname = levelname
        
        return formatted


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with readable formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter with readable format
    formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger instance."""
    return logging.getLogger(name)


# Module-level logger
logger = setup_logger(__name__)


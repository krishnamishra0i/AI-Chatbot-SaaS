import logging
import sys
from pathlib import Path

def setup_logger(name):
    """Setup logger with proper configuration"""
    try:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    except Exception as e:
        print(f"Logger setup failed: {e}")
        return logging.getLogger(name)

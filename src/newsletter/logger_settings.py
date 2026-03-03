# src/beta_user_flow/logger_settings.py
import inspect
import logging
import os
import sys
import warnings
from logging.handlers import RotatingFileHandler

try:
    from pydantic.warnings import UnsupportedFieldAttributeWarning
    warnings.filterwarnings("ignore", category=UnsupportedFieldAttributeWarning)
except ImportError:
    pass

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s - %(filename)s:%(lineno)d:%(funcName)s() - %(message)s"
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOGGER_NAME = "ttqragchat"

def _setup_logger():
    """
    Internal function to set up logger configuration on the ROOT logger.
    This function is idempotent and will not re-configure if already run.
    """
    # Get the root logger. All other loggers will inherit from this.
    logger = logging.getLogger()

    # Prevent adding handlers multiple times
    if getattr(logger, "_is_configured", False):
        return

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)

    info_log_path = os.path.join(LOG_DIR, "info.log")
    error_log_path = os.path.join(LOG_DIR, "error.log")

    # Info handler
    info_handler = RotatingFileHandler(info_log_path, maxBytes=5_000_000, backupCount=3, encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Error handler
    error_handler = RotatingFileHandler(
        error_log_path, maxBytes=5_000_000, backupCount=3, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Stream handler for console output
    stream_handler = logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1))
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Clear any existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(stream_handler)

    # Mark as configured to prevent this from running again
    logger._is_configured = True


def get_logger(name: str = None):
    """
    Get a logger instance. It ensures the root logger is configured first.

    Args:
        name: The name for the logger. If None, it defaults to the
              name of the module that called this function.
    """
    # Ensure the root logger configuration is run once.
    _setup_logger()

    # If no name is provided, use the name of the calling module.
    if name is None:
        caller_frame = inspect.currentframe().f_back
        caller_globals = caller_frame.f_globals
        name = caller_globals.get("__name__", LOGGER_NAME)

    return logging.getLogger(name)

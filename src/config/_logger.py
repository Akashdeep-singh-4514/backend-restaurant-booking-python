# src/config/_logger.py
import logging
import os
import sys

import colorlog  # <--- ADD THIS IMPORT

# Get log file path from environment variable, default to 'app.log'
LOG_FILE = os.getenv("LOG_FILE", "app.log")


def setup_logging():
    """
    Sets up a comprehensive logging configuration.
    Logs to console (INFO level with colors) and a file (DEBUG level).
    """
    logger = logging.getLogger("little_lemon_app")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Console Formatter with colors
        # Define the log colors for different levels
        log_colors = {
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
        # Use ColoredFormatter for the console output
        console_formatter = colorlog.ColoredFormatter(  # <--- CHANGE THIS LINE
            "%(log_color)s%(levelname)s:     %(name)s - %(message)s",  # <--- CHANGE THE FORMAT STRING
            log_colors=log_colors,
            reset=True,
            style="%",
        )

        # Formatter for file output (no colors, as colors are for terminals)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            console_formatter
        )  # <--- USE THE COLORED FORMATTER
        logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Suppress noisy loggers from external libraries
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(
            logging.INFO
        )  # Keep Uvicorn access logs readable
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logger


logger = setup_logging()

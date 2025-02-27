"""
This module sets up logging configuration for the Lunch Menu Comment System.
It ensures the logs directory exists and configures log handlers for both console and file logging.
Additionally, it provides functionality to log HTML content.
"""

import logging
import os

# Ensure logs directory exists
LOG_DIR = "logs"

# Additional logger for HTML logs
html_logger = logging.getLogger("html_logger")

def setup_logging():
    """
    Sets up logging configuration for the application.
    Creates a logs directory if it doesn't exist and configures log handlers.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    # Determine log level based on DEBUG_MODE environment variable
    log_level = logging.DEBUG if os.getenv("DEBUG_MODE") == "1" else logging.WARNING

    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Print logs to console
            logging.FileHandler(f"{LOG_DIR}/lounasvahti.log", encoding="utf-8")  # Main log file
        ]
    )

    # Configure the HTML logger
    html_logger.setLevel(log_level)
    html_handler = logging.FileHandler(f"{LOG_DIR}/html_logs.html", encoding="utf-8")
    html_logger.addHandler(html_handler)

def log_html(file_name, html_content):
    """
    Saves HTML content to a specified log file inside logs/ directory.

    :param file_name: The name of the log file (e.g., "debug.html").
    :param html_content: The HTML content to be logged.
    """
    log_path = os.path.join(LOG_DIR, file_name)

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    html_logger.info(f"Saved HTML log: {log_path}")


"""
This module initializes the Lunch Menu Comment System package.
It sets up logging, defines paths, and loads the configuration from config.ini.
"""

import configparser
import logging
import os

from lounasvahti.logging_config import setup_logging

# Define paths
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))  # lounasvahti/
PROJECT_ROOT = os.path.abspath(os.path.join(PACKAGE_ROOT, ".."))  # lounasvahti's parent (project root)
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.ini")
EXAMPLE_CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.example.ini")

# Setup logging
setup_logging()
logging.info("Logging initialized.")

# Initialize configuration parser
config = configparser.ConfigParser()

def reload_config():
    """Reload configuration from the config.ini file."""
    if not os.path.exists(CONFIG_FILE):
        logging.info("config.ini not found")
        return
    config.read(CONFIG_FILE)
    logging.info("Configuration reloaded from config.ini")

# Load configuration on module import
reload_config()

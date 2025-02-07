import sys
import configparser
import os

PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))  # lounasvahti/
PROJECT_ROOT = os.path.abspath(os.path.join(PACKAGE_ROOT, ".."))  # lounasvahti's parent (project root)

config = configparser.ConfigParser()
config.read(os.path.join(PROJECT_ROOT, "config.ini"))

def reload_config():
    config.read(os.path.join(PROJECT_ROOT, "config.ini"))

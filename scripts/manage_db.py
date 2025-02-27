"""
This script provides command-line interface for managing the database.
Usage:
    manage-db <up|drop|reset>
    manage-db <database_function> <args>
"""

import os
import sys
import logging
from lounasvahti import config
from lounasvahti.database import create_db, drop_db
import lounasvahti.database as db

# Get database path from configuration
DB_PATH = config["database"]["path"]

# Ensure the directory exists
DB_DIR = os.path.dirname(DB_PATH)
if DB_DIR and not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)
    logging.info(f"Created directory for database at {DB_DIR}")

def main():
    if len(sys.argv) < 2:
        print("Usage: manage-db <up|drop|reset>\n   OR: manage-db <database_function> <args>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "up":
        create_db()
        logging.info("Database created.")
    elif command == "drop":
        drop_db()
        logging.info("Database dropped.")
    elif command == "reset":
        drop_db()
        create_db()
        logging.info("Database reset.")
    else:
        try:
            func = getattr(db, command)
            args = sys.argv[2:]
            res = func(*args)
            if res:
                print(res)
                logging.info(f"Executed {command} with result: {res}")
        except AttributeError:
            logging.error(f"Unknown command: {command}")
            print(f"Unknown command: {command}")
    sys.exit(1)

if __name__ == "__main__":
    main()

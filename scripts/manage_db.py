import sys
import os
from lounasvahti import config

DB_PATH = config["database"]["path"]

from lounasvahti.database import create_db, drop_db

# Ensure the directory exists
DB_DIR = os.path.dirname(DB_PATH)
if DB_DIR and not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: manage-db <up|drop|reset>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "up":
        create_db()
        print("Database created.")
    elif command == "drop":
        drop_db()
        print("Database dropped.")
    elif command == "reset":
        drop_db()
        create_db()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()

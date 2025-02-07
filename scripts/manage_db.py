import sys

from lounasvahti.database import create_db, drop_db

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

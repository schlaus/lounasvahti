import sqlite3
from datetime import datetime
from lounasvahti import config

DB_PATH = config["database"]["path"]

def get_conn():
    return sqlite3.connect(DB_PATH)

def create_db():
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE daily_menus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        meal_id INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, meal_id),
        FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        comment TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()

def drop_db():
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS daily_menus")
    cursor.execute("DROP TABLE IF EXISTS meals")
    cursor.execute("DROP TABLE IF EXISTS subscribers")
    
    conn.commit()
    conn.close()

def get_or_create_meal(name):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO meals (name, comment) VALUES (?, NULL) "
        "ON CONFLICT(name) DO NOTHING;",
        (name,)
    )

    cursor.execute("SELECT id FROM meals WHERE name = ?", (name,))
    meal_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return meal_id

def create_menu_item(date, name):
    conn = get_conn()
    cursor = conn.cursor()

    meal_id = get_or_create_meal(name)

    cursor.execute(
        "INSERT INTO daily_menus (date, meal_id) VALUES (?, ?) "
        "ON CONFLICT(date, meal_id) DO NOTHING;",
        (date, meal_id)
    )

    conn.commit()
    conn.close()

def update_meal_comment(name, comment):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE meals SET comment = ? WHERE name = ?",
        (comment, name)
    )

    conn.commit()
    conn.close()

def update_meal_name(old_name, new_name):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE meals SET name = ? WHERE name = ?",
        (new_name, old_name)
    )

    conn.commit()
    conn.close()

def get_menu(date):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT meals.name, meals.comment FROM daily_menus "
        "JOIN meals ON daily_menus.meal_id = meals.id "
        "WHERE date = ?",
        (date,)
    )

    menu = cursor.fetchall()

    conn.close()

    return menu

def add_subscriber(email):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO subscribers (email) VALUES (?) "
        "ON CONFLICT(email) DO NOTHING;",
        (email,)
    )

    conn.commit()
    conn.close()

def remove_subscriber(email):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM subscribers WHERE email = ?",
        (email,)
    )

    conn.commit()
    conn.close()

def remove_menu_item(date):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM daily_menus WHERE date = ?",
        (date,)
    )

    conn.commit()
    conn.close()

def remove_menu_items_before_date(date):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM daily_menus WHERE date < ?",
        (date,)
    )

    conn.commit()
    conn.close()

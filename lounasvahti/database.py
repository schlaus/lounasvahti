"""
This module provides database operations for the Lunch Menu Comment System.
It includes functions to create and drop tables, manage meals, menus, and subscribers.
"""

import os
import sqlite3
import logging

from lounasvahti import config
from lounasvahti.utils import sanitize_comment, get_next_week_workdays

def get_conn():
    """Get a connection to the SQLite database."""
    db_path = os.path.join(config["database"]["path"], "lounasdata.sqlite")
    return sqlite3.connect(db_path)

def create_db():
    """Create the database tables."""
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_menus (
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
        comment TEXT DEFAULT '',
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
    logging.info("Database tables created successfully.")

def drop_db():
    """Drop all the database tables."""
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS daily_menus")
    cursor.execute("DROP TABLE IF EXISTS meals")
    cursor.execute("DROP TABLE IF EXISTS subscribers")
    
    conn.commit()
    conn.close()
    logging.info("Database tables dropped successfully.")

def get_or_create_meal(name):
    """Get or create a meal by name."""
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
    logging.debug(f"Meal '{name}' retrieved or created with ID {meal_id}.")

    return meal_id

def get_meal_by_id(id):
    """Fetch a meal by ID. Returns None if it doesn't exist."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT name, comment FROM meals WHERE id = ?", (id,))
    meal = cursor.fetchone()

    conn.close()
    logging.info(f"Meal with ID {id} fetched: {meal}.")

    return meal  # Returns (name, comment) or None if meal not found

def get_meal_by_name(name):
    """Fetch a meal by name. Returns None if it doesn't exist."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT id, comment FROM meals WHERE name = ?", (name,))
    meal = cursor.fetchone()

    conn.close()
    logging.info(f"Meal with name '{name}' fetched: {meal}.")

    return meal  # Returns (id, comment) or None if meal not found

def create_menu_item(date, name):
    """Create a menu item for a specific date."""
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
    logging.debug(f"Menu item for date {date} and meal '{name}' created.")

def update_meal_comment(meal_id, new_comment):
    """Update the comment for a meal, logging a warning if HTML is detected."""
    conn = get_conn()
    cursor = conn.cursor()

    safe_comment = sanitize_comment(new_comment)

    cursor.execute("UPDATE meals SET comment = ? WHERE id = ?", (safe_comment, meal_id))
    conn.commit()
    conn.close()
    logging.debug(f"Comment for meal ID {meal_id} updated.")

def update_meal_name(old_name, new_name):
    """Update the name of a meal."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE meals SET name = ? WHERE name = ?",
        (new_name, old_name)
    )

    conn.commit()
    conn.close()
    logging.debug(f"Meal name updated from '{old_name}' to '{new_name}'.")

def get_menu(date):
    """Get the menu for a specific date."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT meals.id, meals.name, meals.comment FROM daily_menus "
        "JOIN meals ON daily_menus.meal_id = meals.id "
        "WHERE date = ?",
        (date,)
    )

    menu = cursor.fetchall()

    conn.close()
    logging.debug(f"Menu for date {date} fetched: {menu}.")

    return menu

def add_subscriber(email):
    """Add a new subscriber."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO subscribers (email) VALUES (?) "
        "ON CONFLICT(email) DO NOTHING;",
        (email,)
    )

    conn.commit()
    conn.close()
    logging.info(f"Subscriber with email '{email}' added.")

def remove_subscriber(email):
    """Remove a subscriber."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM subscribers WHERE email = ?",
        (email,)
    )

    conn.commit()
    conn.close()
    logging.info(f"Subscriber with email '{email}' removed.")

def get_subscribers():
    """Get all subscribers."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM subscribers")

    emails = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    logging.debug("Subscribers fetched.")
    return emails

def remove_menu_item(date):
    """Remove a menu item for a specific date."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM daily_menus WHERE date = ?",
        (date,)
    )

    conn.commit()
    conn.close()
    logging.info(f"Menu item for date {date} removed.")

def remove_menu_items_before_date(date):
    """Remove menu items before a specific date."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM daily_menus WHERE date < ?",
        (date,)
    )

    conn.commit()
    conn.close()
    logging.info(f"Menu items before date {date} removed.")

def have_menu_for_next_week():
    """Check if there is a menu for the next week."""
    for day in get_next_week_workdays():
        if get_menu(day):
            logging.debug("Menu found for next week.")
            return True
    logging.debug("No menu found for next week.")
    return False

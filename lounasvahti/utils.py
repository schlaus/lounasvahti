"""
This module provides utility functions for the Lunch Menu Comment System.
It includes date conversions, template loading, and comment sanitization.
"""

import os
import logging
import re
import html

from datetime import date, timedelta, datetime

from lounasvahti import TEMPLATE_DIR

WEEKDAYS = ["maanantai", "tiistai", "keskiviikko", "torstai", "perjantai", "lauantai", "sunnuntai"]

def finnish_date_to_iso(finnish_date):
    """
    Converts a Finnish date format (DD.MM.YYYY) to ISO format (YYYY-MM-DD).
    
    :param finnish_date: Date string in Finnish format (DD.MM.YYYY)
    :return: Date string in ISO format (YYYY-MM-DD)
    """
    try:
        logging.debug(f"Converting Finnish date '{finnish_date}' to ISO format")
        date_obj = datetime.strptime(finnish_date, "%d.%m.%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        logging.error("Invalid date format. Expected format: DD.MM.YYYY")
        raise ValueError("Invalid date format. Expected format: DD.MM.YYYY")

def get_weekday_in_finnish(iso_date):
    """
    Returns the Finnish name of the weekday for a given ISO date (YYYY-MM-DD).
    
    :param iso_date: Date string in ISO format (YYYY-MM-DD)
    :return: Weekday name in Finnish
    """
    try:
        logging.debug(f"Getting Finnish weekday for ISO date '{iso_date}'")
        date_obj = datetime.strptime(iso_date, "%Y-%m-%d")
        return WEEKDAYS[date_obj.weekday()]
    except ValueError:
        logging.error("Invalid date format. Expected format: YYYY-MM-DD")
        raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

def get_next_week_workdays():
    """Get the workdays (Monday to Friday) for the next week."""
    today = date.today()
    next_monday = today + timedelta(days=(7 - today.weekday()))
    workdays = [next_monday + timedelta(days=i) for i in range(5)]
    logging.debug(f"Next week's workdays: {workdays}")
    return [d.strftime('%Y-%m-%d') for d in workdays]

def get_this_week_workdays():
    """Get the workdays (Monday to Friday) for the current week."""
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    workdays = [this_monday + timedelta(days=i) for i in range(5)]
    logging.debug(f"This week's workdays: {workdays}")
    return [d.strftime('%Y-%m-%d') for d in workdays]

def get_monday_and_friday(this_week=False):
    """
    Get the Monday and Friday dates for this week or next week.
    
    :param this_week: Boolean indicating whether to get dates for this week or next week
    :return: Tuple containing Monday and Friday dates in ISO format
    """
    today = date.today()

    if this_week:
        monday = today - timedelta(days=today.weekday())
    else:
        monday = today + timedelta(days=(7 - today.weekday()))

    friday = monday + timedelta(days=4)
    logging.debug(f"Monday and Friday: {monday}, {friday}")
    return monday.strftime('%Y-%m-%d'), friday.strftime('%Y-%m-%d')

def get_today():
    """Get today's date in ISO format."""
    today = date.today().strftime('%Y-%m-%d')
    logging.debug(f"Today's date: {today}")
    return today

def get_tomorrow():
    """Get tomorrow's date in ISO format."""
    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    logging.debug(f"Tomorrow's date: {tomorrow}")
    return tomorrow

def today_is(day):
    """
    Check if today is a specific day of the week.
    
    :param day: Day of the week in Finnish
    :return: Boolean indicating if today is the specified day
    """
    is_today = get_weekday_in_finnish(date.today().isoformat()) == day
    logging.debug(f"Today is {day}: {is_today}")
    return is_today

def load_template(template_name):
    """Loads an email template as a string."""
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    logging.debug(f"Loading template from {template_path}")

    if not os.path.exists(template_path):
        logging.error(f"Template not found: {template_name}")
        raise FileNotFoundError(f"Template not found: {template_name}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def sanitize_comment(comment):
    """Removes HTML tags, trims whitespace, and ensures email-safe text."""
    if not comment:
        return ""

    # Detect if comment contains HTML tags
    if re.search(r"<[^>]+>", comment):
        logging.warning(f"HTML detected in submitted comment: {comment}")

    # Remove all HTML tags
    clean_comment = re.sub(r"<[^>]+>", "", comment)

    # Convert HTML entities to normal characters (&amp; -> &)
    clean_comment = html.unescape(clean_comment)

    # Strip leading/trailing whitespace
    sanitized_comment = clean_comment.strip()
    logging.debug(f"Sanitized comment: {sanitized_comment}")
    return sanitized_comment

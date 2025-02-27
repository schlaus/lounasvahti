"""
This module implements a web server for the Lunch Menu Comment System using Flask.
It provides routes to check the server status and to edit comments for meals.
"""

import logging
import os

from flask import Flask, request, redirect, url_for

from lounasvahti import config
from lounasvahti.database import get_meal_by_id, update_meal_comment
from lounasvahti.utils import load_template

# Load settings from config.ini
HOST = config["server"]["address"]
PORT = int(config["server"]["port"])

# Detect if running under systemd
IS_SYSTEMD = os.getenv("INVOCATION_ID") is not None  # Systemd sets INVOCATION_ID

# HTML snippet to close the window
CLOSER = """
    <script>
        window.close();
    </script>
"""

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def home():
    """Home route to check if the server is running."""
    logging.info("Received request at /")
    return "Lunch Menu Comment System is running!"

@app.route("/comment", methods=["GET", "POST"])
def edit_comment():
    """Route to edit comments for a meal."""
    meal_id = request.args.get("meal_id")  # "meal_id" comes from the email link
    if not meal_id:
        logging.error("Missing meal_id parameter")
        return "Error: Missing meal_id parameter.", 400

    if request.method == "POST":
        new_comment = request.form.get("comment", "").strip()
        logging.info(f"Received new comment for meal_id {meal_id}")

        meal = get_meal_by_id(meal_id)
        if not meal:
            logging.error(f"Meal not found for meal_id {meal_id}")
            return "Error: Meal not found.", 404
        update_meal_comment(meal_id, new_comment)
        logging.info(f"Updated comment for meal_id {meal_id}")

        return redirect(url_for("edit_comment", meal_id=meal_id, close=True))

    # Fetch the meal
    meal = get_meal_by_id(meal_id)
    if not meal:
        logging.error(f"Meal not found for meal_id {meal_id}")
        return "Error: Meal not found.", 404

    meal_name, meal_comment = meal
    meal_comment = meal_comment if meal_comment else ""
    head = CLOSER if request.args.get("close") else ""

    comment_form_template = load_template("comment_form.html")
    logging.info(f"Rendering comment form for meal_id {meal_id}")

    return comment_form_template.format(
        meal_name=meal_name,
        meal_comment=meal_comment,
        head=head
    )

if __name__ == "__main__":
    debug_mode = not IS_SYSTEMD  # Debug mode only when NOT running under systemd
    logging.info(f"Starting web server on {HOST}:{PORT} (Debug: {debug_mode})")
    app.run(host=HOST, port=PORT, debug=debug_mode)

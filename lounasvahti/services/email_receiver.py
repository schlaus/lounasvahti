"""
This module sets up an SMTP server to receive emails and process them.
It handles subscription and unsubscription requests, and updates meal comments
based on the content of the received emails.
"""

import asyncio
import logging
import re
from email import message_from_bytes

from aiosmtpd.controller import Controller
from bs4 import BeautifulSoup

from lounasvahti import config
from lounasvahti.database import update_meal_comment, get_meal_by_name, add_subscriber, remove_subscriber
from lounasvahti.services.email_sender import send_weekly_mail, send_unsubscription_confirmation

# Configuration for the SMTP server
BIND_ADDRESS = config["email_daemon"]["address"]
BIND_PORT = config["email_daemon"]["port"]

class EmailHandler:
    async def handle_DATA(self, server, session, envelope):
        logging.info(f"Received email from: {envelope.mail_from}")
        logging.info(f"To: {envelope.rcpt_tos}")

        # Decode the email message
        msg = message_from_bytes(envelope.content)

        # Extract plain text content, fallback to HTML if necessary
        text = self.extract_text(msg)
        logging.info(f"Extracted message:\n{text}")

        # Check for control words (subscription or unsubscription)
        first_word = self.get_first_word(text)
        if first_word:
            if first_word.lower() == "tilaa":
                logging.info(f"Subscription request from {envelope.mail_from}")
                self.handle_subscription(envelope.mail_from)
                return "250 OK"
            elif first_word.lower() == "lopeta":
                logging.info(f"Unsubscription request from {envelope.mail_from}")
                self.handle_unsubscription(envelope.mail_from)
                return "250 OK"

        # Process the extracted text to get meal_name and new_comment
        meal_name, new_comment = self.parse_comment(text)
        if meal_name and new_comment:
            logging.info(f"Meal Name: {meal_name}")
            logging.info(f"New Comment: {new_comment}")
            meal_id, _ = get_meal_by_name(meal_name)
            if meal_id:
                update_meal_comment(meal_id, new_comment)
            else:
                logging.warning("Meal not found in database.")
        else:
            logging.warning("Could not extract a valid comment.")

        return "250 OK"

    def extract_text(self, msg):
        """
        Extracts the plain text content from an email.
        If no plain text is found, it falls back to extracting from HTML.
        """
        text = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    text = part.get_payload(decode=True).decode(part.get_content_charset(), errors="replace")
                    break
                elif content_type == "text/html" and text is None:
                    html = part.get_payload(decode=True).decode(part.get_content_charset(), errors="replace")
                    text = self.strip_html(html)  # Convert HTML to plain text if no text/plain part is found
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                text = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors="replace")
            elif content_type == "text/html":
                html = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors="replace")
                text = self.strip_html(html)

        return text.strip() if text else "(No readable content found)"

    def strip_html(self, html):
        """
        Removes HTML tags from a given HTML string and returns plain text.
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n").strip()

    def get_first_word(self, text):
        """Extracts the first word from the email text."""
        match = re.match(r"^\s*([\wåäöÅÄÖ]+)", text)  # Match first word (including Finnish characters)
        return match.group(1) if match else None

    def parse_comment(self, text):
        """
        Extracts the meal name (first line) and the new comment (everything after "Kommentti:").
        Ignores quoted replies and signatures.
        """
        lines = text.splitlines()

        # Extract meal name (first non-empty line)
        meal_name = next((line.strip() for line in lines if line.strip()), None)
        if not meal_name:
            return None, None  # No valid meal name found

        # Find "Kommentti:" and extract everything after it
        new_comment = None
        for i, line in enumerate(lines[1:], start=1):  # Start from second line
            if line.strip().startswith("Kommentti:"):
                new_comment = line.split("Kommentti:", 1)[1].strip()  # Take everything after "Kommentti:"
                # If the next lines are part of the comment, include them
                for extra_line in lines[i + 1 :]:
                    if extra_line.strip().startswith(">") or re.match(r"On .* wrote:", extra_line):
                        break  # Stop at quoted replies
                    elif len(extra_line.strip()) == 0:
                        break  # Break after empty line
                    new_comment += "\n" + extra_line.strip()
                break

        return meal_name, new_comment if new_comment else None

    def handle_subscription(self, email):
        """Handles subscription requests."""
        logging.info(f"Adding {email} to subscribers.")
        add_subscriber(email)
        send_weekly_mail(email, True)

    def handle_unsubscription(self, email):
        """Handles unsubscription requests."""
        logging.info(f"Removing {email} from subscribers.")
        remove_subscriber(email)
        send_unsubscription_confirmation(email)

def receive_email_blocking():
    """
    Runs the SMTP server in a blocking manner for debugging from the terminal.
    """
    controller = Controller(EmailHandler(), hostname=BIND_ADDRESS, port=BIND_PORT)
    controller.start()
    logging.info(f"SMTP server running on {BIND_ADDRESS}:{BIND_PORT}... Press Ctrl+C to stop.")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down SMTP server...")
    finally:
        controller.stop()
        loop.close()

if __name__ == "__main__":
    logging.info("Email receiver starting.")
    receive_email_blocking()  # Run in terminal for testing

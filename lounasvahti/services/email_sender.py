"""
This module provides functionalities for composing and sending emails related to lunch menus.
It includes functions to generate mailto links, compose daily and weekly emails, and send emails
to specified recipients. Additionally, it handles unsubscription confirmations.
"""

import logging
import smtplib
import urllib.parse
from email.message import EmailMessage

from lounasvahti import config
from lounasvahti.database import get_menu
from lounasvahti.logging_config import log_html
from lounasvahti.utils import (
    get_next_week_workdays,
    get_this_week_workdays,
    get_today,
    get_weekday_in_finnish,
    load_template,
)

def generate_mailto_link(meal_name, comment):
    """
    Generates a properly encoded mailto link.
    
    :param meal_name: The name of the meal (may contain special characters)
    :param comment: The meal comment (can be None)
    :return: A correctly formatted mailto link
    """
    logging.debug("Generating mailto link for meal: %s", meal_name)
    # Ensure comment is not None
    comment = comment if comment else ""

    # Properly encode subject and body to handle spaces, ampersands, etc.
    subject = urllib.parse.quote(f"Kommentti: {meal_name}")
    body = urllib.parse.quote(f"{meal_name}\nKommentti: {comment}")

    return f"mailto:{config['smtp']['reply_to']}?subject={subject}&body={body}"

def generate_unsubscribe_link():
    """
    Generates an unsubscribe link for the email footer.
    """
    logging.debug("Generating unsubscribe link")
    return f"mailto:{config['smtp']['reply_to']}?subject=lopeta&body=lopeta"

def compose_weekly_mail(this_week=False):
    """
    Composes the weekly email content.
    
    :param this_week: Boolean indicating if the email is for this week or next week.
    :return: Formatted email content.
    """
    logging.info("Composing weekly mail, this_week=%s", this_week)
    if this_week:
        workdays = get_this_week_workdays()
        title = "Tämän viikon lounaslista"
    else:
        workdays = get_next_week_workdays()
        title = "Ensi viikon lounaslista"
    content = "\n".join([compose_menu_for_day(d) for d in workdays])
    email_template = load_template("email_template.html")
    unsubscribe_link = generate_unsubscribe_link()
        
    return email_template.format(title=title, content=content, unsubscribe_link=unsubscribe_link)

def compose_daily_mail():
    """
    Composes the daily email content.
    
    :return: Formatted email content.
    """
    logging.info("Composing daily mail")
    content = compose_menu_for_day(get_today())
    email_template = load_template("email_template.html")
    unsubscribe_link = generate_unsubscribe_link()
    
    return email_template.format(title=f"Päivän lounas {get_today()}", content=content, unsubscribe_link=unsubscribe_link)

def compose_menu_for_day(date):
    """
    Composes the menu for a specific day.
    
    :param date: The date for which to compose the menu.
    :return: Formatted menu content.
    """
    logging.debug("Composing menu for day: %s", date)
    day_name = get_weekday_in_finnish(date)
    menu_items = get_menu(date)

    meal_template = load_template("meal_template.html")
    content = ""
    for (meal_id, name, comment) in menu_items:
        comment = comment if comment else ""
        mailto_link = generate_mailto_link(name, comment)
        server_url = config["server"]["url"]
        content += meal_template.format(meal_id=meal_id, name=name, comment=comment, mailto_link=mailto_link, server_url=server_url)
    
    day_template = load_template("day_template.html")
    
    return day_template.format(name=day_name, date=date, content=content)

def send_mail(subject, content, recipients):
    """
    Sends an email with the given subject and content to the specified recipients.
    
    :param subject: The subject of the email.
    :param content: The content of the email.
    :param recipients: A list of recipient email addresses.
    """
    logging.info("Sending mail with subject: %s", subject)
    if type(recipients) is str:
        recipients = [recipients]
    
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config["smtp"]["email"]
    msg["Reply-To"] = config["smtp"]["reply_to"]
    msg["To"] = ", ".join(recipients)
    msg.set_content(content, subtype="html")
    try:
        with smtplib.SMTP_SSL(config["smtp"]["server"], config["smtp"]["port"]) as smtp_server:
            smtp_server.login(config["smtp"]["email"], config["smtp"]["password"])
            smtp_server.send_message(msg, config["smtp"]["email"], recipients)
        logging.info("Mail sent successfully to %s", recipients)
    except Exception as e:
        logging.error("Failed to send mail: %s", e)

def send_weekly_mail(recipients, this_week=False, dry_run=False):
    """
    Sends the weekly email to the specified recipients.
    
    :param recipients: A list of recipient email addresses.
    :param this_week: Boolean indicating if the email is for this week or next week.
    :param dry_run: Boolean indicating if the email should actually be sent or just logged.
    """
    logging.info("Sending weekly mail, this_week=%s", this_week)
    content = compose_weekly_mail(this_week)
    subject = "Tämän viikon lounaslista" if this_week else "Ensi viikon lounaslista"    
    if dry_run:
        logging.info("Dry run enabled, not sending weekly mail")
        logging.info("Recipients: %s", recipients)
        logging.info("Subject: %s", subject)
        log_html("weekly.html", content)
        logging.info("Content logged to weekly.html")
        return
    send_mail(subject, content, recipients)

def send_daily_mail(recipients, dry_run=False):
    """
    Sends the daily email to the specified recipients.
    
    :param recipients: A list of recipient email addresses.
    :param dry_run: Boolean indicating if the email should actually be sent or just logged.
    """
    logging.info("Sending daily mail")
    content = compose_daily_mail()
    subject = "Päivän lounas"
    if dry_run:
        logging.info("Dry run enabled, not sending daily mail")
        logging.info("Recipients: %s", recipients)
        logging.info("Subject: %s", subject)
        log_html("daily.html", content)
        logging.info("Content logged to daily.html")
        return
    send_mail(subject, content, recipients)

def send_unsubscription_confirmation(email):
    """
    Sends an unsubscription confirmation email to the specified address.
    
    :param email: The email address to send the confirmation to.
    """
    logging.info("Sending unsubscription confirmation to %s", email)
    subject = "Vahvistus tilauksen lopetuksesta"
    content = "Tilaus on lopetettu onnistuneesti. Voit tilata uudelleen lähettämällä sähköpostin, jonka sisältönä on 'tilaa'."
    send_mail(subject, content, email)

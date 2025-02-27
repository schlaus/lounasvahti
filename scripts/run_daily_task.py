"""
This script runs Lounasvahti's daily tasks, including scraping the menu for the next week
and sending daily or weekly emails to subscribers.
"""

import argparse
import logging
from lounasvahti.database import have_menu_for_next_week, get_subscribers, create_menu_item
from lounasvahti.services.scraper import Scraper
import lounasvahti.services.email_sender as email
from lounasvahti.utils import today_is

def main():
    parser = argparse.ArgumentParser(description="Runs Lounasvahti's daily tasks.")
    parser.add_argument(
        "--scrape", action="store_true", help="Scrape menu for next week"
    )
    parser.add_argument(
        "--for", help="Run tasks for DAY [mon-sun|ma-su]", dest="day"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't send emails"
    )
    args = parser.parse_args()

    should_scrape = args.scrape or not have_menu_for_next_week()
    is_sunday = today_is("sunnuntai") or (args.day and args.day.lower() in ["su", "sunnuntai", "sun", "sunday"])
    is_saturday = today_is("lauantai") or (args.day and args.day.lower() in ["la", "lauantai", "sat", "saturday"])
    dry_run = args.dry_run

    logging.info("Running daily task.")
    
    if should_scrape:
        logging.debug("Scraping menu for next week.")
        scraper = Scraper()
        menu = scraper.get_menu()
        for date, items in menu.items():
            for item in items:
                logging.debug(f"Creating menu item for {date}: {item}")
                create_menu_item(date, item)

    if is_sunday:
        logging.info("Today is Sunday, no emails will be sent.")
        return

    subscribers = get_subscribers()

    if not subscribers:
        logging.warning("No subscribers found.")
        return

    if is_saturday:
        logging.info("Today is Saturday, sending weekly email.")
        email.send_weekly_mail(subscribers, dry_run=dry_run)
    else:
        logging.info("Sending daily email.")
        email.send_daily_mail(subscribers, dry_run=dry_run)

if __name__ == "__main__":
    main()


"""
This script fetches and prints the menu for this or next week using the Scraper service.
"""

import argparse
import logging
from lounasvahti.services.scraper import Scraper

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch and print the menu for this or next week.")
    parser.add_argument(
        "--this-week", action="store_true", help="Fetch this week's menu instead of next week's."
    )
    args = parser.parse_args()

    logging.info("Starting the scraper")

    # Initialize scraper and fetch menu
    scraper = Scraper()
    menu = scraper.get_menu(this_week=args.this_week)

    logging.info("Menu fetched successfully")

    # Print the scraped menu
    for date, items in menu.items():
        print(f"{date}:")
        for item in items:
            print(f"  - {item}")

    logging.info("Menu printed successfully")

if __name__ == "__main__":
    main()

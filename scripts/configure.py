"""
This module handles the configuration setup for the Lounasvahti application.
It ensures the configuration file exists, prompts the user for target configuration,
updates the configuration file, and optionally installs services.
"""

import os
import shutil
import logging
import inquirer
from lounasvahti import CONFIG_FILE, EXAMPLE_CONFIG_FILE, config, reload_config

def ensure_config_exists():
    """Ensure config.ini exists by copying config.example.ini if necessary."""
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(EXAMPLE_CONFIG_FILE):
            shutil.copy(EXAMPLE_CONFIG_FILE, CONFIG_FILE)
            logging.info(f"Created {CONFIG_FILE} from {EXAMPLE_CONFIG_FILE}.")
            reload_config()
        else:
            logging.error(f"Error: {EXAMPLE_CONFIG_FILE} is missing. Cannot proceed.")
            exit(1)
    else:
        logging.info(f"{CONFIG_FILE} already exists.")

def update_config():
    """Update the config file with the new values."""
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)
    logging.info("Configuration updated successfully!")

def prompt_target_config():
    """Prompt the user to configure the target settings."""
    from lounasvahti.services.scraper import Scraper
    
    scraper = Scraper()
    
    # Prompt for target URL
    target_url = config["target"]["url"]
    target_url = inquirer.text(message=f"Target URL [{target_url}]") or target_url
    scraper.set_url(target_url)
    
    # Prompt for restaurant type
    restaurant_types = scraper.get_restaurant_types()
    restaurant_type_name = config["target"]["type"]
    restaurant_type_name = inquirer.list_input(message="Select restaurant type", choices=restaurant_types.keys(), default=restaurant_type_name)
    restaurant_type_uuid = restaurant_types[restaurant_type_name]
    scraper.set_restaurant_type(restaurant_type_name, restaurant_type_uuid)
    
    # Prompt for restaurant
    restaurants = scraper.get_restaurants()
    restaurant_name = config["target"]["name"]
    restaurant_name = inquirer.list_input(message="Select restaurant", choices=restaurants.keys(), default=restaurant_name)
    restaurant_uuid = restaurants[restaurant_name]
    scraper.set_restaurant(restaurant_name, restaurant_uuid)

def prompt_service_install():
    """Ask the user if they want to install services now."""
    response = inquirer.list_input(message="Would you like to install the app's services now?", choices=["yes", "no"], default="yes")
    
    if response == "yes":
        logging.info("Running service installation script...")
        os.system("venv/bin/python install_services.py")  # Use 'python' instead of 'bash' if it's a Python script
    else:
        logging.info("To install services later, run the following command manually:")
        logging.info("  bin/lounasvahti install_services")

def main():
    """Main function to run the configuration setup."""
    ensure_config_exists()
    prompt_target_config()
    update_config()
    prompt_service_install()

if __name__ == "__main__":
    main()

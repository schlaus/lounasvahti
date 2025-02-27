"""
This module provides a Scraper class for extracting lunch menu data from a specified website.
It includes methods for setting the target URL, selecting restaurant types and restaurants,
and retrieving the menu for a given week. The scraper uses BeautifulSoup for parsing HTML
and requests for making HTTP requests.
"""

import json
import logging
import os
import re

import requests
from bs4 import BeautifulSoup

from lounasvahti import config
from lounasvahti.utils import finnish_date_to_iso

class Scraper:

    RESTAURANT_TYPE_SELECT = "ctl00$MainContent$RestaurantTypeDropDownList"
    RESTAURANT_SELECT = "ctl00$MainContent$RestaurantDropDownList"
    LANGUAGE_SELECT = "ctl00$MainContent$LanguagesDropDownList"
    WEEK_SELECT = "ctl00$MainContent$ShowMenuDropDownList"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    LANGUAGE = "fi"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        self.state = None
        self.url = None
        self.data_file = os.path.join(config["database"]["path"], "scraper_data.json")
        self.data = {
            "url": None,
            "endpoint": None,
            "restaurant_type_name": None,
            "restaurant_type_uuid": None,
            "restaurant_name": None,
            "restaurant_uuid": None
        }
        self.state_vars = {}
        self.temp_data = {}
        self._load_data()
        logging.info("Scraper initialized")

    def _load_data(self):
        """Load stored data from a JSON file, ensuring required keys exist."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logging.info("Data loaded from file")
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
            logging.warning("Data file not found or invalid JSON, initializing with empty data")
        
        self.data = {key: data.get(key) for key in self.data.keys()}
    
    def _save_data(self):
        """Save stored data to a JSON file."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        logging.info("Data saved to file")

    def _get_state_vars(self, response_text):
        """Extract state variables from the HTML response."""
        soup = BeautifulSoup(response_text, "html.parser")
        for fieldset in soup.find_all(class_="aspNetHidden"):
            for input_tag in fieldset.find_all("input"):
                self.state_vars[input_tag["name"]] = input_tag["value"]
        logging.debug("State variables updated")

    def _get(self, *args, **kwargs):
        """Perform a GET request and update state variables."""
        response = self.session.get(*args, **kwargs)
        response.raise_for_status()
        self._get_state_vars(response.text)
        logging.info(f"GET request to {response.url} successful")
        return response

    def _post(self, *args, data={}, **kwargs):
        """Perform a POST request and update state variables."""
        data = {**self.state_vars, **data}
        response = self.session.post(*args, data=data, **kwargs)
        response.raise_for_status()
        self._get_state_vars(response.text)
        logging.info(f"POST request to {response.url} successful")
        return response

    def _find_menu_in_soup(self, soup):
        """Find the menu in the HTML soup."""
        menu = {}
        for data_panel in soup.find_all("div", class_="DayDataPanel"):
            logging.debug("Scraping data panel")
            header = data_panel.find("div", class_="emenu_tab_panel_header")
            iso_date = finnish_date_to_iso(header.get_text(strip=True)[3:])
            logging.debug("Scraping menu for date: %s", iso_date)
            
            for row in data_panel.find_all("div", class_="emenu_tab_panel_row"):
                menu_item = ", ".join(
                    item.get_text(strip=True)
                    for item in row.find_all(id=re.compile("SecureLabelDish"))
                )
                if iso_date not in menu:
                    menu[iso_date] = []
                menu[iso_date].append(menu_item)
                logging.debug(f"Found item for date {iso_date}: {menu_item}")

        logging.debug("Menu scrape completed")
        return menu

    def get_menu(self, this_week=False):
        """Get the menu for the selected restaurant."""
        url = self.data["endpoint"]
        self._get(url)
        ctl = "1" if this_week else "2"
        data = {
            self.RESTAURANT_TYPE_SELECT: self.data["restaurant_type_uuid"],
            self.RESTAURANT_SELECT: self.data["restaurant_uuid"],
            self.LANGUAGE_SELECT: self.LANGUAGE,
            self.WEEK_SELECT: "0" if this_week else "1",
            "__EVENTTARGET": f"ctl00$MainContent$RestaurantDateRangesFilterHeadersDataList$ctl0{ctl}$RestaurantDateRangesFilterHeadersLinkButton",
            "ctl00$ScriptManager1": f"ctl00$MasterUpdatePanel|ctl00$MainContent$RestaurantDateRangesFilterHeadersDataList$ctl0{ctl}$RestaurantDateRangesFilterHeadersLinkButton",
            "ctl00$MainContent$DropDownListGetWeeks:": 1
        }
        response = self._post(url, data=data)
        soup = BeautifulSoup(response.text, "html.parser")
        menu = self._find_menu_in_soup(soup)
        logging.info("Menu retrieved successfully")
        return menu

    def get_restaurant_types(self):
        """Get a list of restaurant types from the target site."""
        url = self.data["url"]
        response = self._get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        restaurant_types = soup.find("select", {"name": self.RESTAURANT_TYPE_SELECT}).find_all("option")
        logging.info("Restaurant types retrieved successfully")
        return {option.text: option["value"] for option in restaurant_types if option["value"]}

    def get_restaurants(self):
        """Get a list of restaurants for the selected restaurant type."""
        url = self.data["url"]
        restaurant_type_uuid = self.data["restaurant_type_uuid"]
        data = self.data
        data[self.RESTAURANT_TYPE_SELECT] = restaurant_type_uuid
        response = self._post(url, data=data)
        soup = BeautifulSoup(response.text, "html.parser")
        restaurants = soup.find("select", {"name": self.RESTAURANT_SELECT}).find_all("option")
        logging.info("Restaurants retrieved successfully")
        return {option.text: option["value"] for option in restaurants if option["value"]}

    def set_url(self, url):
        """Set the target URL."""
        self.data["url"] = url
        self._save_data()
        logging.info(f"URL set to {url}")
    
    def set_restaurant_type(self, name, uuid):
        """Set the restaurant type."""
        self.data["restaurant_type_name"] = name
        self.data["restaurant_type_uuid"] = uuid
        self._save_data()
        logging.info(f"Restaurant type set to {name} with UUID {uuid}")

    def set_restaurant(self, name, uuid):
        """Set the restaurant."""
        self.data["restaurant_name"] = name
        self.data["restaurant_uuid"] = uuid

        data = {
            self.RESTAURANT_TYPE_SELECT: self.data["restaurant_type_uuid"],
            self.RESTAURANT_SELECT: self.data["restaurant_uuid"]
        }

        response = self._post(self.data["url"], data=data)
        self.data["endpoint"] = response.url
        self._save_data()
        logging.info(f"Restaurant set to {name} with UUID {uuid}")

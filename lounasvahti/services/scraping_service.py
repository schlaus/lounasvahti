import requests
from bs4 import BeautifulSoup
import re
from lounasvahti import config
from lounasvahti.utils import finnish_date_to_iso
from lounasvahti.database import create_menu_item

URL = config["target"]["url"]

def scrape_menu(this_week=False):

    state_for_next_week = {
        "ctl00$ScriptManager1": "ctl00$MasterUpdatePanel|ctl00$MainContent$RestaurantDateRangesFilterHeadersDataList$ctl02$RestaurantDateRangesFilterHeadersLinkButton",
        "ctl00$MainContent$LanguagesDropDownList": "fi",
        "ctl00$MainContent$ShowDinerGroupDropDownList": "9c955f7d-50bd-48c1-89e8-ea1a58f8eb34",
        "ctl00$MainContent$RestaurantTypeDropDownList": "790987cb-0243-472d-9880-72b9136c50f1",
        "ctl00$MainContent$RestaurantDropDownList": "842c5111-5acb-47f5-b4c4-8df6cbd2e3bf",
        "ctl00$MainContent$DropDownListGetWeeks": "1",
        "ctl00$MainContent$ShowMenuDropDownList": "2",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl00$MealHeader_FirstOpenState": "",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl00$MealHeader_State": "1",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl01$MealHeader_FirstOpenState": "",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl01$MealHeader_State": "1"
    }

    state_for_this_week = {
        "ctl00$ScriptManager1": "ctl00$MasterUpdatePanel|ctl00$MainContent$ShowMenuDropDownList",
        "ctl00$MainContent$LanguagesDropDownList": "fi",
        "ctl00$MainContent$ShowDinerGroupDropDownList": "9c955f7d-50bd-48c1-89e8-ea1a58f8eb34",
        "ctl00$MainContent$RestaurantTypeDropDownList": "790987cb-0243-472d-9880-72b9136c50f1",
        "ctl00$MainContent$RestaurantDropDownList": "842c5111-5acb-47f5-b4c4-8df6cbd2e3bf",
        "ctl00$MainContent$DropDownListGetWeeks": "1",
        "ctl00$MainContent$ShowMenuDropDownList": "1",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl00$MealHeader_FirstOpenState": "",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl00$MealHeader_State": "1",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl01$MealHeader_FirstOpenState": "",
        "ctl00$MainContent$WeekdayListView$ctrl0$Meals$ctl01$MealHeader_State": "1"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    session = requests.Session()
    response = session.get(URL)

    soup = BeautifulSoup(response.text, "html.parser")

    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    viewstate_generator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    event_validation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]

    state_data = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstate_generator,
        "__EVENTVALIDATION": event_validation,
        "__EVENTTARGET": "ctl00$MainContent$Dropdown",
        "__EVENTARGUMENT": "",
        "__ASYNCPOST": "true"
    }

    data = state_data | (state_for_this_week if this_week else state_for_next_week)

    response = session.post(URL, data=data, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    for data_panel in soup.find_all("div", class_="DayDataPanel"):
        header = data_panel.find("div", class_="emenu_tab_panel_header")
        iso_date = finnish_date_to_iso(header.get_text(strip=True)[3:])
        
        for row in data_panel.find_all("div", class_="emenu_tab_panel_row"):
            create_menu_item(iso_date, ", ".join(
                    item.get_text(strip=True)
                    for item in row.find_all(id=re.compile("SecureLabelDish"))
                )
            )

if __name__ == "__main__":
    scrape_menu()


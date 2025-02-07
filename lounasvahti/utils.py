from datetime import date, timedelta, datetime
import locale

def finnish_date_to_iso(finnish_date: str) -> str:
    """
    Converts a Finnish date format (DD.MM.YYYY) to ISO format (YYYY-MM-DD).
    
    :param finnish_date: Date string in Finnish format (DD.MM.YYYY)
    :return: Date string in ISO format (YYYY-MM-DD)
    """
    try:
        date_obj = datetime.strptime(finnish_date, "%d.%m.%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Expected format: DD.MM.YYYY")

def get_weekday_in_finnish(iso_date: str) -> str:
    """
    Returns the Finnish name of the weekday for a given ISO date (YYYY-MM-DD).
    
    :param iso_date: Date string in ISO format (YYYY-MM-DD)
    :return: Weekday name in Finnish
    """
    try:
        locale.setlocale(locale.LC_TIME, "fi_FI.UTF-8")
        date_obj = datetime.strptime(iso_date, "%Y-%m-%d")
        return date_obj.strftime("%A")
    except ValueError:
        raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

def get_next_week_workdays() -> list[str]:
    today = date.today()
    next_monday = today + timedelta(days=(7 - today.weekday()))
    workdays = [next_monday + timedelta(days=i) for i in range(5)]
    return [d.strftime('%Y-%m-%d') for d in workdays]

def get_tomorrow() -> str:
    tomorrow = date.today() + timedelta(days=1)
    return tomorrow.strftime('%Y-%m-%d')

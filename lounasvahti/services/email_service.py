import asyncio
from aiosmtpd.controller import Controller
from email.message import EmailMessage
from lounasvahti import config
from lounasvahti.database import get_menu
from lounasvahti.utils import get_weekday_in_finnish, get_next_week_workdays, get_tomorrow

BIND_ADDRESS = config["daemon"]["address"]
BIND_PORT = config["daemon"]["port"]

class EmailHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"Received email from {envelope.mail_from}")
        print(f"To: {envelope.rcpt_tos}")
        print(f"Message:\n{envelope.content.decode()}")
        # Process email content
        return "250 OK"

def compose_weekly_mail():
    workdays = get_next_week_workdays()
    email_content = ""
    
    for workday in workdays:
        weekday_name = get_weekday_in_finnish(workday)
        menu_items = get_menu(workday)
        
        email_content += f"{weekday_name} ({workday})\n"
        for item in menu_items:
            email_content += f"{item[0]}\nKommentti: {item[1]}\n\n"
    
    return email_content

def compose_daily_mail():
    tomorrow = get_tomorrow()
    weekday_name = get_weekday_in_finnish(tomorrow)
    menu_items = get_menu(tomorrow)
    
    email_content = f"{weekday_name} ({tomorrow})\n"
    for item in menu_items:
        email_content += f"{item[0]}\nKommentti: {item[1]}\n\n"
    
    return email_content

def receive_email_blocking():
    controller = Controller(EmailHandler(), hostname=BIND_ADDRESS, port=BIND_PORT)
    print("Starting SMTP server... Press Ctrl+C to stop.")
    try:
        controller.run()  # This blocks until manually stopped
    except KeyboardInterrupt:
        controller.stop()

def send_mail(subject, content, recipients):
    pass

if __name__ == "__main__":
    receive_email_blocking()


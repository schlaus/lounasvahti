import asyncio
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
from lounasvahti import config
from lounasvahti.services.email_service import EmailHandler

BIND_ADDRESS = config["daemon"]["address"]
BIND_PORT = config["daemon"]["port"]


class SMTPServer(Controller):
    """Manages the SMTP server instance."""
    
    def __init__(self, handler):
        super().__init__(handler, hostname=BIND_ADDRESS, port=BIND_PORT)
    
    def start(self):
        logging.info("Starting SMTP server...")
        super().start()
    
    def stop(self):
        logging.info("Stopping SMTP server...")
        super().stop()

# Global instance of the controller
server = SMTPServer(EmailHandler())

async def start():
    """Starts the SMTP daemon asynchronously."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, server.start)

async def stop():
    """Stops the SMTP daemon asynchronously."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, server.stop)

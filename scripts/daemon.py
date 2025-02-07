import sys
import signal
import asyncio
import logging

from lounasvahti.services.daemon_service import start, stop

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def handle_signal(signum, frame):
    """Gracefully stop the daemon on SIGTERM or SIGINT."""
    logging.info(f"Received signal {signum}. Stopping daemon...")
    loop.run_until_complete(stop())  # Ensure proper shutdown
    loop.stop()
    sys.exit(0)

# Attach signal handlers
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

if __name__ == "__main__":
    logging.info("Starting Lounasvahti Daemon...")
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Stopping daemon...")
        loop.run_until_complete(stop())
    finally:
        loop.close()
        logging.info("Daemon stopped.")

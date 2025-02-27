"""
This script installs or updates systemd services and timers for the Lounasvahti project.
"""

import getpass
import os
import subprocess

# Get absolute paths
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON_EXEC = os.path.join(PROJECT_PATH, "venv", "bin", "python")
SYSTEMD_DIR = os.path.join(PROJECT_PATH, "systemd")

def generate_service_file(template_filename):
    """
    Reads a .template file, replaces placeholders, and returns the processed content.
    """
    if not template_filename.endswith(".template"):
        raise ValueError(f"Expected a .template file, got {template_filename}")

    # Define paths
    template_path = os.path.join(SYSTEMD_DIR, template_filename)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Service template {template_filename} not found!")

    # Read the template
    with open(template_path, "r") as template_file:
        service_content = template_file.read()

    # Replace placeholders
    service_content = service_content.replace("{{USER}}", getpass.getuser())
    service_content = service_content.replace("{{PROJECT_PATH}}", PROJECT_PATH)
    service_content = service_content.replace("{{PYTHON_EXEC}}", PYTHON_EXEC)

    return service_content

def install_or_update_service(template_filename, restart=False):
    """
    Installs or updates a systemd service/timer by replacing placeholders and copying it.
    If the service already exists, it will be updated.
    """
    service_filename = template_filename.replace(".template", "")
    service_dest = f"/etc/systemd/system/{service_filename}"

    service_content = generate_service_file(template_filename)

    # Write the processed file to a temporary location
    temp_path = f"/tmp/{service_filename}"
    with open(temp_path, "w") as service_file:
        service_file.write(service_content)

    # If the service already exists, check for differences
    if os.path.exists(service_dest):
        with open(service_dest, "r") as existing_file:
            existing_content = existing_file.read()
        
        if existing_content == service_content:
            print(f"[INFO] {service_filename} is already up to date.")
            return

        print(f"[INFO] Updating {service_filename}...")

    else:
        print(f"[INFO] Installing {service_filename}...")

    # Move the service file to the systemd directory
    subprocess.run(["sudo", "mv", temp_path, service_dest], check=True)

    # Reload systemd to recognize changes
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", service_filename], check=True)

    if restart:
        print(f"[INFO] Restarting {service_filename}...")
        subprocess.run(["sudo", "systemctl", "restart", service_filename], check=True)

    print(f"[SUCCESS] {service_filename} installed/updated.")

def install_services():
    """
    Installs or updates both the main daemon service and the daily task timer.
    """
    install_or_update_service("lounasvahti-email.service.template", restart=True)  # SMTP service
    install_or_update_service("lounasvahti-web.service.template", restart=True)  # Web service
    install_or_update_service("lounasvahti-daily.service.template", restart=False)
    install_or_update_service("lounasvahti-daily.timer.template", restart=False)

    # Start the timer so it begins running
    subprocess.run(["sudo", "systemctl", "start", "lounasvahti-daily.timer"], check=True)

    print("[SUCCESS] Systemd services and timers installed/updated successfully!")

if __name__ == "__main__":
    install_services()

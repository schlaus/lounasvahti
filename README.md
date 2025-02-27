> If it's worth doing, it's worth overdoing.
>
> -- <cite>Adam Savage</cite>

Lounasvahti is a LMCS (Lunch Menu Comment System) designed to scrape data from the Palvelukeskus Helsinki eRuokalista service, and send weekly and daily e-mails to tell you what's for lunch. On workdays you get the day's menu at 6 o'clock. On Saturdays you get the whole menu for next week so you can prepare. You can comment on each meal by (1) sending an e-mail with your comment or (2) via a web form. The e-mails contain links for both. You can manage subscriptions by e-mail or from the terminal.

## Installation

Follow these steps to set up Lounasvahti LMCS on your system:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/schlaus/lounasvahti.git
    cd lounasvahti
    ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure the application:**
    ```bash
    bin/lounasvahti configure
    ```

5. **(optional) Install or update the services & timer:**
   ```bash
   bin/lounasvahti install_services
   ```

## Usage

Once Lounasvahti is up and running, you can subscribe to the e-mails by sending an e-mail with "tilaa" in the body to the e-mail server the app is configured to listen to. You'll get the current week's menu as a reply. The local part (name of the mailbox) doesn't matter because the e-mail server listens on all of them. To stop the messages, send another message with "lopeta" in the body. The subject of the messages does not matter.

To send a comment via e-mail, simply click on the "Lähetä kommentti" button in an e-mail the app has sent. Alternatively, you can send an e-mail with the exact name of the menu item on the first row of the body, and "Kommentti:" on the second. Everything after that is considered part of the comment until an empty line or the beginning of a quoted message is reached. HTML is not allowed in comments. Currently, you can't clear a comment (save an empty comment) by e-mail, but it works via the form.

To run any of the scripts manually, use the provided `lounasvahti` script:

```bash
bin/lounasvahti <script_name> [arguments...]
```

### Available Scripts

- **configure**: Sets up the configuration for the application.
    ```bash
    bin/lounasvahti configure
    ```

- **install_services**: Installs or updates systemd services and timers.
    ```bash
    bin/lounasvahti install_services
    ```

- **run_daily_task**: Runs the daily tasks, including scraping the menu and sending emails.
    ```bash
    bin/lounasvahti run_daily_task [--scrape] [--for DAY] [--dry-run]
    ```

- **manage_db**: Provides a command-line interface for managing the database.
    ```bash
    bin/lounasvahti manage_db <up|drop|reset|database_function> [args]
    ```

    #### Practical examples:
    
    To manually add a subscriber:
    ```bash
    bin/lounasvahti manage_db add_subscriber your.email@example.com
    ```

    To remove a subscriber:
    ```bash
    bin/lounasvahti manage_db remove_subscriber your.email@example.com
    ```

- **fetch_menu**: Fetches and prints the menu for this or next week.
    ```bash
    bin/lounasvahti fetch_menu [--this-week]
    ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

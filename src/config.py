"""
Stores application configuration.

Responsible for:
- Loading environment variables
- Defining tracker settings
- Validating required configuration
"""

import os
from dotenv import load_dotenv


class Config:
    """
    Central location for application settings.
    """

    def __init__(self):
        load_dotenv()

        # API credentials
        self.ebay_client_id = os.getenv("EBAY_CLIENT_ID")
        self.ebay_client_secret = os.getenv("EBAY_CLIENT_SECRET")

        # Discord webhook URL
        self.discord_webhook_url = os.getenv(
            "DISCORD_WEBHOOK_URL"
        )

        # Search settings
        self.search_query = "MacBook Pro M1 Pro"
        self.max_price = 550

        # How often eBay is checked
        self.check_every_seconds = 300

        # Stores IDs of previously-seen listings
        self.seen_file = "seen_items.json"

        self.validate()

    def validate(self):
        """
        Ensures all required settings exist before startup.
        """

        if not self.ebay_client_id:
            raise ValueError("EBAY_CLIENT_ID missing")

        if not self.ebay_client_secret:
            raise ValueError("EBAY_CLIENT_SECRET missing")

        if not self.discord_webhook_url:
            raise ValueError("DISCORD_WEBHOOK_URL missing")
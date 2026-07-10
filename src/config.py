import os
from dotenv import load_dotenv

from src.search_category import SearchCategory


class Config:
    def __init__(self):
        load_dotenv()

        # =====================================================
        # eBay API Credentials (supports multiple API keys)
        # =====================================================

        self.ebay_credentials = [
            {
                "client_id": os.getenv("EBAY_CLIENT_ID_1"),
                "client_secret": os.getenv("EBAY_CLIENT_SECRET_1"),
            },
            {
                "client_id": os.getenv("EBAY_CLIENT_ID_2"),
                "client_secret": os.getenv("EBAY_CLIENT_SECRET_2"),
            },
            {
                "client_id": os.getenv("EBAY_CLIENT_ID_3"),
                "client_secret": os.getenv("EBAY_CLIENT_SECRET_3"),
            },
        ]

        # Remove empty credentials
        self.ebay_credentials = [
            cred
            for cred in self.ebay_credentials
            if cred["client_id"] and cred["client_secret"]
        ]

        # =====================================================
        # Discord
        # =====================================================

        self.discord_webhook_url = os.getenv(
            "DISCORD_WEBHOOK_URL"
        )

        self.discord_auction_webhook_url = os.getenv(
            "DISCORD_AUCTION_WEBHOOK_URL"
        )

        # =====================================================
        # Tracker Settings
        # =====================================================

        self.check_every_seconds = 300

        self.seen_file = os.getenv(
            "SEEN_ITEMS_FILE",
            "/app/data/seen_items.json",
        )

        # =====================================================
        # Common banned words
        # =====================================================

        self.banned_words = [
            "case",
            "cover",
            "screen protector",
            "keyboard",
            "charger",
            "box only",
            "for parts",
            "for part",
            "spares",
            "repair",
            "faulty",
            "fault",
            "icloud",
            "locked",
            "broken",
            "damaged",
            "cracked",
            "non-working",
            "azerty",
            "qwertz",
            "grade d",
            "smashed screen",
            "display issue",
            "water damage",
            "read description",
            "lines on screen",
            "dead battery",
            "bad battery",
            "screen lines",
        ]

        # =====================================================
        # Search Categories
        # =====================================================

        self.search_categories = [

            # ---------------------------------
            # MacBook Pro M1
            # ---------------------------------

            SearchCategory(
                name="MacBook Pro M1",
                query="MacBook Pro M1",
                max_price=450,
                required_words=[
                    "macbook",
                    "pro",
                    "m1",
                ],
                banned_words=self.banned_words + [
                    "m1 pro",
                    "m1 max",
                ],
            ),

            # ---------------------------------
            # MacBook Pro M1 Pro
            # ---------------------------------

            SearchCategory(
                name="MacBook Pro M1 Pro",
                query="MacBook Pro M1 Pro",
                max_price=600,
                required_words=[
                    "macbook",
                    "pro",
                    "m1 pro",
                ],
                banned_words=self.banned_words,
            ),

            # ---------------------------------
            # MacBook Pro M1 Max
            # ---------------------------------

            SearchCategory(
                name="MacBook Pro M1 Max",
                query="MacBook Pro M1 Max",
                max_price=700,
                required_words=[
                    "macbook",
                    "pro",
                    "m1 max",
                ],
                banned_words=self.banned_words,
            ),

            # ---------------------------------
            # MacBook Pro M2 Pro
            # ---------------------------------

            SearchCategory(
                name="MacBook Pro M2 Pro",
                query="MacBook Pro M2 Pro",
                max_price=850,
                required_words=[
                    "macbook",
                    "pro",
                    "m2 pro",
                ],
                banned_words=self.banned_words,
            ),

            # ---------------------------------
            # MacBook Air M1
            # ---------------------------------

            SearchCategory(
                name="MacBook Air M1",
                query="MacBook Air M1",
                max_price=400,
                required_words=[
                    "macbook",
                    "air",
                    "m1",
                ],
                banned_words=self.banned_words,
            ),

            # ---------------------------------
            # MacBook Air M2
            # ---------------------------------

            SearchCategory(
                name="MacBook Air M2",
                query="MacBook Air M2",
                max_price=600,
                required_words=[
                    "macbook",
                    "air",
                    "m2",
                ],
                banned_words=self.banned_words,
            ),
        ]

        self.validate()

    def validate(self):

        if not self.ebay_credentials:
            raise ValueError(
                "No eBay API credentials found."
            )

        if not self.discord_webhook_url:
            raise ValueError(
                "DISCORD_WEBHOOK_URL missing"
            )

        if not self.discord_auction_webhook_url:
            raise ValueError(
                "DISCORD_AUCTION_WEBHOOK_URL missing"
            )
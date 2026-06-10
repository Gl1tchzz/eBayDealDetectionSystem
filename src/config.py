import os
from dotenv import load_dotenv
from src.search_category import SearchCategory


class Config:
    def __init__(self):
        load_dotenv()

        self.ebay_client_id = os.getenv("EBAY_CLIENT_ID")
        self.ebay_client_secret = os.getenv("EBAY_CLIENT_SECRET")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

        self.check_every_seconds = 300
        self.seen_file = "seen_items.json"

        self.banned_words = [
            "case",
            "cover",
            "screen protector",
            "keyboard",
            "charger",
            "box only",
            "for parts",
            "spares",
            "repair",
            "faulty",
            "icloud",
            "locked",
            "broken",
            "damaged",
            "cracked",
            "non-working",
            "AZERTY",
            "QWERTZ",
            "grade d"
        ]

        self.search_categories = [
            SearchCategory(
                name="MacBook Pro M1 Pro",
                query="MacBook Pro M1 Pro",
                max_price=600,
                required_words=["macbook", "pro", "m1"],
                banned_words=self.banned_words,
            ),
            SearchCategory(
                name="MacBook Pro M1 Max",
                query="MacBook Pro M1 Max",
                max_price=750,
                required_words=["macbook", "pro", "m1", "max"],
                banned_words=self.banned_words,
            ),
            SearchCategory(
                name="MacBook Pro M2 Pro",
                query="MacBook Pro M2 Pro",
                max_price=850,
                required_words=["macbook", "pro", "m2"],
                banned_words=self.banned_words,
            ),
            SearchCategory(
                name="MacBook Air M1",
                query="MacBook Air M1",
                max_price=300,
                required_words=["macbook", "air", "m1"],
                banned_words=self.banned_words,
            ),
            SearchCategory(
                name="MacBook Air M2",
                query="MacBook Air M2",
                max_price=600,
                required_words=["macbook", "air", "m2"],
                banned_words=self.banned_words,
            ),
        ]

        self.validate()

    def validate(self):
        if not self.ebay_client_id:
            raise ValueError("EBAY_CLIENT_ID missing")

        if not self.ebay_client_secret:
            raise ValueError("EBAY_CLIENT_SECRET missing")

        if not self.discord_webhook_url:
            raise ValueError("DISCORD_WEBHOOK_URL missing")